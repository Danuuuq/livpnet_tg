import asyncio
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, status
from faststream.rabbit.fastapi import RabbitRouter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.variables import SettingServers
from app.crud.user import user_crud
from app.crud.server import server_crud, certificate_crud
from app.crud.subscription import subscription_crud, price_crud
from app.core.log_config import log_action_status
from app.models.payment import Payment
from app.models.server import Certificate, Server
from app.models.subscription import (
    Subscription,
    SubscriptionDuration,
    SubscriptionType,
)
from app.models.user import User
from app.schemas.payment import PaymentAnswer
from app.schemas.subscription import (
    CertificateCreateDB,
    SubscriptionDB,
    SubscriptionCreate,
    SubscriptionCreateDB,
    SubscriptionRenew,
    SubscriptionUpdate,
    SubscriptionNotifyDB,
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
        """Проверка наличия пользователя и подписки с возвратом."""
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
        headers = settings.get_headers_auth
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

    @staticmethod
    def get_end_date(
        duration: SubscriptionDuration | None,
        sub_end_date: datetime | None = None
    ) -> datetime:
        if duration is None:
            time_delta = timedelta(days=3)
        elif duration is SubscriptionDuration.month_1:
            time_delta = timedelta(days=30)
        elif duration is SubscriptionDuration.month_6:
            time_delta = timedelta(days=182)
        elif duration is SubscriptionDuration.year_1:
            time_delta = timedelta(days=365)
        if (sub_end_date is None or
            sub_end_date < datetime.now(timezone.utc).replace(tzinfo=None)):
            return datetime.now(timezone.utc).replace(tzinfo=None) + time_delta
        return sub_end_date + time_delta

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
        sub_data = SubscriptionCreateDB(
            user_id=user.id,
            region_id=server.region_id,
            type=subscription_type,
            protocol=server.protocol,
            is_active=True,
            end_date=self.get_end_date(subscription_duration),
        )
        subscription = await subscription_crud.create(sub_data, session)
        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Подписка для {user.telegram_id} не создана!'
            )
        await self.create_cert_in_db(
            server,
            cert_links,
            subscription,
            session,
            vless,
        )
        log_action_status(
            action_name='Создание подписки',
            message=(f'Подписка создана для пользователя {user.telegram_id}'
                     f' с {len(cert_links)} сертификатами')
        )
        return subscription

    async def create_cert_in_db(
        self,
        server: Server,
        cert_links: list[str],
        subscription: Subscription,
        session: AsyncSession,
        vless: str | None = None,
    ) -> None:
        for link in cert_links:
            cert_data = CertificateCreateDB(
                filename=link,
                url_vless=vless,
                server_id=server.id,
                subscription_id=subscription.id,
            )
            await certificate_crud.create(cert_data, session)

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
        headers = settings.get_headers_auth
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
        data_in: SubscriptionCreate | SubscriptionRenew,
        user: User,
        session: AsyncSession,
        type_sub: SubscriptionType | None = None,
        region: str | None = None,
    ) -> PaymentAnswer:
        type_sub = data_in.type or type_sub
        price = await price_crud.get_by_type_and_duration(
            data_in.duration,
            type_sub,
            session,
        )
        if price is None:
            log_action_status(
                action_name='Наличие цен на подписку!',
                message=(f'По данным параметрам: {data_in.duration}, '
                         f'{type_sub} нет доступных подписок')
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(f'По данным параметрам: {data_in.duration}, '
                        f'{type_sub} нет доступных подписок')
            )
        url = await create_payment(price, data_in, user, session)
        if isinstance(data_in, SubscriptionCreate):
            return PaymentAnswer(
                amount=price,
                type=data_in.type,
                duration=data_in.duration,
                region_code=data_in.region_code,
                protocol=data_in.protocol,
                url=url,
            )
        elif isinstance(data_in, SubscriptionRenew):
            return PaymentAnswer(
                amount=price,
                type=type_sub,
                duration=data_in.duration,
                region_code=region,
                url=url,
            )

    async def action_after_payment(
        self,
        payment: Payment,
        session: AsyncSession,
    ) -> None:
        """Действия после оплаты подписки.

        Есть id подписки но не указан протокол или тип, то это продление.
        Есть id подписки и протокол или тип, то это изменение подписки.
        Если нет id подписки, то это создание новой подписки.
        """
        if (payment.intent_data.get('sub_id') and
            not payment.intent_data.get('protocol') and
            not payment.intent_data.get('type')):
            data_renew = SubscriptionRenew(
                tg_id=payment.user.telegram_id,
                **payment.intent_data,
            )
            await self.renewal_sub(data_renew, session)
        elif (payment.intent_data.get('sub_id') and
              (payment.intent_data.get('protocol') or
               payment.intent_data.get('type'))):
            data_in = SubscriptionUpdate(
                tg_id=payment.user.telegram_id,
                **payment.intent_data,
            )
            log_action_status(
                action_name='Обновление подписки',
                message=(f'Обновление подписки {data_in.sub_id} '
                         f'пользователя {payment.user.telegram_id}!')
            )
            await self.update_sub(data_in, payment.user, session)
        else:
            data_in = SubscriptionCreate(
                tg_id=payment.user.telegram_id,
                **payment.intent_data,
            )
            await self.process_create(data_in, payment.user, session)

    async def update_sub(
        self,
        data_in: SubscriptionUpdate,
        user: User,
        session: AsyncSession,
    ) -> None:
        sub_db = await subscription_crud.get_by_id(data_in.sub_id, session)
        if sub_db is None:
            log_action_status(
                action_name='Обновление подписки',
                message=f'Подписка {data_in.sub_id} не найдена!'
            )
            raise HTTPException(
                status_code=404,
                detail=f'Подписка {data_in.sub_id} не найдена!'
            )
        region_changed = (data_in.region_code and data_in.region_code != 
                          sub_db.region.code)
        protocol_changed = (data_in.protocol and data_in.protocol !=
                            sub_db.certificates[0].server.protocol)
        type_changed = data_in.type and data_in.type != sub_db.type

        if region_changed or protocol_changed:
            async with AsyncClient() as client:
                for cert in sub_db.certificates:
                    await self.delete_certificate(cert, client, session)
            cert_links, active_server = await self.get_server_and_certs(
                data_in,
                user,
                session
            )
            sub_db.is_active = True
            sub_db.end_date = self.get_end_date(
                data_in.duration,
                sub_db.end_date,
            )
            sub_db.region = active_server.region_id
            sub_db.type = data_in.type
            session.add(sub_db)
            await self.create_cert_in_db(
                active_server,
                cert_links,
                sub_db,
                session,
            )

        elif type_changed:
            if sub_db.certificates:
                server = await server_crud.get_by_id(
                    sub_db.certificates[0].server_id,
                    session,
                )
            else:
                server = await self.check_active_server(
                    sub_db.protocol,
                    sub_db.region.code,
                    session,
                )
            device_count = {
                SubscriptionType.trial: 1,
                SubscriptionType.devices_2: 2,
                SubscriptionType.devices_4: 4
            }
            old_count = len(sub_db.certificates)
            new_count = device_count.get(data_in.type, 1)
            sub_db.is_active = True
            sub_db.end_date = self.get_end_date(
                data_in.duration,
                sub_db.end_date,
            )
            sub_db.type = data_in.type
            session.add(sub_db)
            if new_count > old_count:
                delta = new_count - old_count
                cert_names = [uuid4().hex for _ in range(delta)]
                cert_tasks = [
                    self.request_certificate(server, name)
                    for name in cert_names
                ]
                cert_links = await asyncio.gather(*cert_tasks)
                await self.create_cert_in_db(
                    server,
                    cert_links,
                    sub_db,
                    session,
                )
            elif new_count < old_count:
                to_remove = sub_db.certificates[new_count:]
                async with AsyncClient() as client:
                    for cert in to_remove:
                        await self.delete_certificate(cert, client, session)
        else:
            if not sub_db.certificates:
                device_count = {
                    SubscriptionType.trial: 1,
                    SubscriptionType.devices_2: 2,
                    SubscriptionType.devices_4: 4
                }
                server = await self.check_active_server(
                    sub_db.protocol,
                    sub_db.region.code,
                    session,
                )
                cert_names = [uuid4().hex for _ in range(device_count.get(sub_db.type, 1))]
                cert_tasks = [
                    self.request_certificate(server, name)
                    for name in cert_names
                ]
                cert_links = await asyncio.gather(*cert_tasks)
                await self.create_cert_in_db(
                    server,
                    cert_links,
                    sub_db,
                    session,
                )
            sub_db.is_active = True
            sub_db.end_date = self.get_end_date(
                data_in.duration,
                sub_db.end_date,
            )
            session.add(sub_db)
        await session.commit()

    async def renewal_sub(
        self,
        data_in: SubscriptionRenew,
        session: AsyncSession,
    ) -> None:
        sub_db = await subscription_crud.get_by_id(data_in.sub_id, session)
        if sub_db is None:
            log_action_status(
                action_name='Продление подписки',
                message=f'Подписка {data_in.sub_id} не найдена!'
            )
            raise HTTPException(
                status_code=404,
                detail=f'Подписка {data_in.sub_id} не найдена!'
            )

        if not sub_db.certificates:
            device_count = {
                SubscriptionType.trial: 1,
                SubscriptionType.devices_2: 2,
                SubscriptionType.devices_4: 4
            }
            server = await self.check_active_server(
                sub_db.protocol,
                sub_db.region.code,
                session,
            )
            cert_names = [uuid4().hex for _ in range(device_count.get(sub_db.type, 1))]
            cert_tasks = [
                self.request_certificate(server, name)
                for name in cert_names
            ]
            cert_links = await asyncio.gather(*cert_tasks)
            await self.create_cert_in_db(
                server,
                cert_links,
                sub_db,
                session,
            )
        sub_db.is_active = True
        sub_db.end_date = self.get_end_date(data_in.duration, sub_db.end_date)
        session.add(sub_db)
        await session.commit()

    async def get_server_and_certs(
        self,
        data_in: SubscriptionCreate,
        user: User,
        session: AsyncSession,
    ) -> tuple[list[str], Server]:
        active_server = await self.check_active_server(
            data_in.protocol,
            data_in.region_code,
            session,
        )
        device_count = {
            SubscriptionType.trial: 1,
            SubscriptionType.devices_2: 2,
            SubscriptionType.devices_4: 4
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
        cert_links = await asyncio.gather(*cert_tasks)
        return cert_links, active_server

    async def process_create(
        self,
        data_in: SubscriptionCreate,
        user: User,
        session: AsyncSession,
    ) -> SubscriptionDB:
        cert_links, active_server = await self.get_server_and_certs(
            data_in,
            user,
            session,
        )
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
            is_active=subscription.is_active,
            id=subscription.id,
            region=subscription.region,
            type=subscription.type,
            end_date=subscription.end_date,
            certificates=cert_links,
        )
        return subs_answer

    async def pay_update_subscription(
        self,
        data_in: SubscriptionRenew | SubscriptionCreate,
        session: AsyncSession,
    ) -> PaymentAnswer:
        user, subs = await self.check_user_and_subscription(
            data_in.tg_id,
            session,
        )
        if subs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(f'Подписка {data_in.sub_id} не найдена у '
                        f'пользователя {data_in.tg_id}!')
            )
        subscription = next((s for s in subs if s.id == data_in.sub_id), None)
        if isinstance(data_in, SubscriptionRenew):
            return await self.create_link(
                data_in,
                user,
                session,
                subscription.type,
                subscription.region.code,
            )
        elif isinstance(data_in, SubscriptionCreate):
            return await self.create_link(data_in, user, session)

    async def notify_about_subs(
        self,
        session: AsyncSession,
        router: RabbitRouter,
    ) -> None:
        expired_subs = await subscription_crud.get_expired_subs(
            session,
        )
        expiring_subs = await subscription_crud.get_expiring_subs(
            session,
        )
        for sub in expired_subs:
            try:
                sub.is_active = False
                session.add(sub)
                await self.revoke_certificate(sub, session)
                log_action_status(
                    action_name='Деактивация подписки',
                    message=(f'Подписка ID={sub.id} пользователя {sub.user_id}'
                             ' деактивирована и сертификаты удалены.')
                )
            except Exception as e:
                log_action_status(
                    action_name='Ошибка при деактивации',
                    error=e,
                    message=f'Не удалось обработать подписку ID={sub.id}'
                )
            else:
                log_action_status(
                    action_name='Создание задачи',
                    message=(f'Уведомление {sub.user.telegram_id} '
                             'об отключении подписки ID={sub.id}.')
                )
                await router.broker.publish(
                    message=SubscriptionNotifyDB(
                        type=sub.type,
                        region=sub.region.name,
                        protocol=sub.protocol,
                        telegram_id=sub.user.telegram_id),
                    queue='notify_deactivate_sub',
                )
        for sub in expiring_subs:
            log_action_status(
                action_name='Создание задачи',
                message=(f'Уведомление {sub.user.telegram_id} '
                         'об окончании подписки ID={sub.id}.')
            )
            await router.broker.publish(
                message=SubscriptionNotifyDB(
                    type=sub.type,
                    region=sub.region.name,
                    protocol=sub.protocol,
                    telegram_id=sub.user.telegram_id),
                queue='notify_end_sub',
            )
        await session.commit()
        return None

    async def delete_certificate(
        self,
        cert: Certificate,
        http_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        headers = settings.get_headers_auth
        parsed = urlparse(cert.filename)
        domain = parsed.netloc
        filename = os.path.basename(parsed.path)
        cert_name, _ = os.path.splitext(filename)
        url = f'https://{domain}/{SettingServers.API_CERT_HOOK}/{cert_name}'
        response = await http_client.delete(url, headers=headers)
        if response.status_code != 200:
            log_action_status(
                action_name='Ошибка удаления сертификата',
                message=(f'Не удалось удалить сертификат {cert_name} с сервера'
                         f' {domain}. Код ответа: {response.status_code}, '
                         f'тело: {response.text}')
            )
            raise HTTPException(
                status_code=502,
                detail=f'Ошибка при удалении сертификата {cert_name}'
            )
        log_action_status(
            action_name='Удаление сертификата',
            message=(f'Сертификат {cert_name} успешно удален'
                        f' на сервере {domain}')
        )
        await certificate_crud.delete(cert, session)

    async def revoke_certificate(
        self,
        subscription: Subscription,
        session: AsyncSession,
    ) -> None:
        if subscription.is_active:
            raise HTTPException(
                status_code=403,
                detail='Нельзя удалить сертификаты у активной подписки!'
            )
        certificates = subscription.certificates
        async with AsyncClient() as client:
            for cert in certificates:
                await self.delete_certificate(cert, client, session)
        log_action_status(
            action_name='Удаление сертификатов',
            message=f'Удалены сертификаты по подписке {subscription.id} '
        )

    async def get_sub_with_cert(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> list[SubscriptionDB]:
        user, subscriptions = await self.check_user_and_subscription(
            tg_id,
            session,
        )
        if subscriptions is None:
            raise HTTPException(
                status_code=404,
                detail=f'Нет подписок у пользователя {user.telegram_id}!'
            )
        subs_answer = []
        for subscription in subscriptions:
            subs_answer.append(SubscriptionDB(
                is_active=subscription.is_active,
                id=subscription.id,
                type=subscription.type,
                protocol=subscription.protocol,
                region=subscription.region,
                end_date=subscription.end_date.date(),
                certificates=[cert.filename
                              for cert in subscription.certificates],
            ))
        return subs_answer


subscription_service = SubscriptionService()
