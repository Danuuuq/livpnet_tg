import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.variables import SettingServers
from app.crud.payment import payment_crud
from app.crud.user import user_crud
from app.crud.server import server_crud, certificate_crud
from app.crud.subscription import subscription_crud, price_crud
from app.core.log_config import log_action_status
from app.models.server import Server
from app.models.subscription import (
    Subscription,
    SubscriptionDuration,
    SubscriptionType,
)
from app.models.user import User
from app.schemas.payment import PaymentAnswer, YooKassaWebhookNotification
from app.schemas.subscription import (
    CertificateCreateDB,
    SubscriptionDB,
    SubscriptionCreate,
    SubscriptionCreateDB,
    SubscriptionRenew,
)
from app.services.payment import create_payment


class SubscriptionService:
    """Логика действий с пользователями."""

    model = Subscription
    crud = subscription_crud

    async def check_user_and_subscription(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> tuple[User, Subscription | None]:
        user = await user_crud.get_by_tg_id(tg_id, session)
        if user:
            return user, user.subscription
        elif user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден!'
            )
        return user, None

    async def request_certificate(
        self,
        active_server: Server,
        name: str,
    ) -> str:
        """Отправка запроса на генерацию сертификата."""
        headers = {'Authorization': f'Bearer {settings.API_KEY}'}
        url = (f'https://{active_server.domain_name}'
               f'/{SettingServers.API_CERT_HOOK}')
        json_payload = {'name': name}
        async with AsyncClient() as client:
            response = await client.post(
                url, headers=headers, json=json_payload)
            if response.status_code != 201:
                log_action_status(
                    action_name='Ошибка генерации сертификата',
                    message=f'Ответ сервера: {response.text} '
                )
                raise HTTPException(
                    status_code=502,
                    detail=f'Ошибка генерации сертификата: {response.text}'
                )
            data = response.json()
            log_action_status(
                action_name='Запрос сертификата',
                message=(f'Сертификат {name} успешно сгенерирован'
                         f' на сервере {active_server.domain_name}')
            )
            return data.get('download_url')

    async def create_subscription(
        self,
        server: Server,
        user: User,
        cert_links: list[str],
        session: AsyncSession,
        subscription_type: SubscriptionType = SubscriptionType.trial,
        subscription_duration: SubscriptionDuration | None = None,
        vless: str | None = None,
    ) -> Subscription | None:
        """Создание первой подписки с сертификатами."""
        if subscription_duration is None:
            time_delta = timedelta(days=3)
        elif subscription_duration is SubscriptionDuration.month_1:
            time_delta = timedelta(days=30)
        elif subscription_duration is SubscriptionDuration.month_6:
            time_delta = timedelta(days=182)
        elif subscription_duration is SubscriptionDuration.year_1:
            time_delta = timedelta(days=365)
        sub_data = SubscriptionCreateDB(
            user_id=user.id,
            region_id=server.region_id,
            type=subscription_type,
            is_active=True,
            end_date=(datetime.now(timezone.utc).replace(tzinfo=None) +
                      time_delta),
        )
        subscription = await subscription_crud.create(sub_data, session)
        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Подписка для {user.telegram_id} не создана!'
            )

        # Создание записи о сертификатах
        for link in cert_links:
            cert_data = CertificateCreateDB(
                filename=link,
                url_vless=vless,
                server_id=server.id,
                subscription_id=subscription.id,
            )
            await certificate_crud.create(cert_data, session)
        log_action_status(
            action_name='Создание пробной подписки',
            message=(f'Подписка создана для пользователя {user.telegram_id}'
                     f' с {len(cert_links)} сертификатами')
        )
        return subscription

    async def check_active_server(
        self,
        protocol: str,
        region_code: str,
        session: AsyncSession,
    ) -> Server:
        active_servers = await server_crud.get_server_region_and_protocol(
            region_code, protocol, session)
        if active_servers is None:
            log_action_status(
                action_name='Наличие доступных серверов!',
                message=(f'Отсутствуют сервера: протокол {protocol} '
                         f'регион {region_code}')
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f'Отсутствуют сервера: протокол {protocol} '
                        f'регион {region_code}')
            )
        active_server = None
        headers = {'Authorization': f'Bearer {settings.API_KEY}'}
        for check_server in active_servers:
            url = (f'https://{check_server.domain_name}'
                   f'/{SettingServers.API_CHECK_HEALTH}')
            async with AsyncClient() as client:
                response = await client.get(url, headers=headers)
                data = response.json()
                if response.status_code != 200:
                    log_action_status(
                        action_name='Проверка доступности сервера',
                        message=f'Сервер {check_server.domain_name} недоступен'
                    )
                    continue
                elif data.get('status') == SettingServers.API_OK_HEALTH:
                    active_server = check_server
                    break
        if active_server is None:
            log_action_status(
                action_name='Проверка доступности серверов',
                message=(f'Сервера не отвечают. Протокол: {protocol} '
                         f'локация: {region_code}')
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=('Не удалось получить ответа от серверов! '
                        f'Протокол: {protocol} '
                        f'локация: {region_code}')
            )
        return active_server

    async def trial_or_payment(
        self,
        data_in: SubscriptionCreate,
        session: AsyncSession,
    ) -> SubscriptionDB | PaymentAnswer:
        user, subscription = await self.check_user_and_subscription(
            data_in.tg_id,
            session,
        )
        if data_in.type == SubscriptionType.trial and subscription:
            log_action_status(
                action_name='Наличие подписки!',
                message=f'Подписка уже есть у {user.telegram_id}'
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=('Подписка уже есть у пользователя! '
                        'Пробную подписку повторно не оформить.')
            )
        elif data_in.type == SubscriptionType.trial:
            return await self.process_create(data_in, user, session)
        else:
            return await self.create_link(data_in, user, session)

    async def create_link(
        self,
        data_in: SubscriptionCreate,
        user: User,
        session: AsyncSession,
    ) -> PaymentAnswer:
        price = await price_crud.get_by_type_and_duration(
            data_in.duration, data_in.type, session
        )
        if price is None:
            log_action_status(
                action_name='Наличие цен на подписку!',
                message=(f'По данным параметрам: {data_in.duration}, '
                         f'{data_in.type} нет доступных подписок')
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(f'По данным параметрам: {data_in.duration}, '
                        f'{data_in.type} нет доступных подписок')
            )
        url = await create_payment(price, data_in, user, session)
        return PaymentAnswer(
            amount=price,
            type=data_in.type,
            duration=data_in.duration,
            region_code=data_in.region_code,
            protocol=data_in.protocol,
            url=url,
        )

    async def create_after_payment(
        self,
        data_in: YooKassaWebhookNotification,
        session: AsyncSession,
    ) -> SubscriptionDB:
        operation_id = data_in.object.id
        payment = await payment_crud.get_by_operation_id(operation_id, session)
        data_in = SubscriptionCreate(tg_id=payment.user.telegram_id, **payment.intent_data)
        return await self.process_create(data_in, payment.user, session)

    async def process_create(
        self,
        data_in: SubscriptionCreate,
        user: User,
        session: AsyncSession,
    ) -> SubscriptionDB:
        active_server = await self.check_active_server(
            data_in.protocol,
            data_in.region_code,
            session,
        )
        device_count = {
            'trial': 1,
            '2_devices': 2,
            '4_devices': 4
        }.get(data_in.type, 1)
        cert_names = [uuid4().hex for _ in range(device_count)]
        log_action_status(
            action_name='Запрос подписки',
            message=(f'Генерация {device_count} сертификатов '
                     f'для пользователя {user.telegram_id}')
        )
        cert_tasks = [
            self.request_certificate(active_server, name)
            for name in cert_names
        ]
        # cert_links: list[str] = await asyncio.gather(*cert_tasks)
        cert_links: list[str] = ['https://ya.ru/3']
        try:
            subscription = await self.create_subscription(
                server=active_server,
                user=user,
                cert_links=cert_links,
                session=session,
                subscription_type=data_in.type,
                subscription_duration=data_in.duration,
            )

        except Exception as e:
            log_action_status(
                error=e,
                action_name='Ошибка создания подписки'
            )
            raise
        subs_answer = SubscriptionDB(
            id=subscription.id,
            region=subscription.region,
            type=subscription.type,
            end_date=subscription.end_date,
            certificates=cert_links,
        )
        return subs_answer

    async def update_subscription(
        self,
        data_in: SubscriptionRenew| SubscriptionCreate,
        session: AsyncSession,
    ) -> PaymentAnswer:
        user, subs = await self.check_user_and_subscription(
            data_in.tg_id,
            session,
        )
        subscription = next((s for s in subs if s.id == data_in.sub_id), None)
        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f'Подписка {data_in.sub_id} не найдена у '
                        f'пользователя {data_in.tg_id}!')
            )
        base_data = SubscriptionCreate.model_validate(subscription, update={
            'tg_id': user.tg_id,
            'sub_id': subscription.id,
            # Подменяем только переданные значения (если они есть)
            'duration': getattr(data_in, 'duration', subscription.duration),
            'type': getattr(data_in, 'type', subscription.type),
            'region_code': getattr(data_in, 'region_code', subscription.region.code),
            'protocol': getattr(data_in, 'protocol', subscription.protocol),
        })
        return await self.create_link(base_data, user, session)

    async def deactivate_subscription(
        self,
        session: AsyncSession,
    ) -> list[SubscriptionDB]:
        expired_subs = await subscription_crud.get_expired_subscriptions(session)
        for sub in expired_subs:
            try:
                sub.is_active = False
                session.add(sub)
                await self.revoke_certificate(sub, session)
                log_action_status(
                    action_name='Деактивация подписки',
                    message=f'Подписка ID={sub.id} пользователя {sub.user_id} деактивирована и сертификаты удалены.'
                )
            except Exception as e:
                log_action_status(
                    action_name='Ошибка при деактивации',
                    error=e,
                    message=f'Не удалось обработать подписку ID={sub.id}'
                )
        await session.commit()
        return expired_subs
        

    async def revoke_certificate(
        self,
        subscription: Subscription,
        session: AsyncSession,
    ) -> None:
        headers = {'Authorization': f'Bearer {settings.API_KEY}'}
        if subscription.is_active:
            raise HTTPException(
                status_code=403,
                detail='Нельзя удалить сертификаты у активной подписки!'
            )
        certificates = subscription.certificates
        async with AsyncClient() as client:
            for cert in certificates:
                parsed = urlparse(cert.filename)
                domain = parsed.netloc
                filename = os.path.basename(parsed.path)
                cert_name, _ = os.path.splitext(filename)
                url = f'https://{domain}/{SettingServers.API_CERT_HOOK}/{cert_name}'
                response = await client.delete(url, headers=headers)
                if response.status_code != 204:
                    log_action_status(
                        action_name='Ошибка удаления сертификата',
                        message=(f'Не удалось удалить сертификат {cert_name} с сервера '
                                f'{domain}. Код ответа: {response.status_code}, тело: {response.text}')
                    )
                    raise HTTPException(
                        status_code=502,
                        detail=f'Ошибка при удалении сертификата {cert_name}'
                    )
                await certificate_crud.delete(cert, session)
        log_action_status(
            action_name='Удаление сертификатов',
            message=f'Удалены сертификаты по подписке {subscription.id} '
        )

    async def get_sub_with_cert(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> list[SubscriptionDB]:
        user, subscriptions = await self.check_user_and_subscription(tg_id, session)
        subs_answer = []
        for subscription in subscriptions:
            subs_answer.append(SubscriptionDB(
                id=subscription.id,
                type=subscription.type,
                region=subscription.region,
                end_date=subscription.end_date.date(),
                certificates=[cert.filename for cert in subscription.certificates],
            ))
        return subs_answer


subscription_service = SubscriptionService()
