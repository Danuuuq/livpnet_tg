import asyncio
from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.variables import SettingServers
from app.crud.user import user_crud
from app.crud.server import server_crud, certificate_crud
from app.crud.subscription import subscription_crud
from app.core.log_config import log_action_status
from app.models.server import Certificate, Server
from app.models.subscription import Subscription, SubscriptionDuration, SubscriptionType
from app.models.user import User
from app.schemas.subscription import (
    CertificateCreateDB,
    SubscriptionDB,
    SubscriptionCreate,
    SubscriptionCreateDB,
)
from app.validators.base import get_or_404


class SubscriptionService:
    """Логика действий с пользователями."""

    model = Subscription
    crud = subscription_crud

    async def check_subscription(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> tuple[User, Subscription | None]:
        user = await user_crud.get_by_tg_id(tg_id, session)
        if user:
            subscription = await subscription_crud.get_by_user(
                user.id, session)
            return user, subscription
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

    async def create(
        self,
        data_in: SubscriptionCreate,
        session: AsyncSession,
    ) -> SubscriptionDB:
        user, subscription = await self.check_subscription(data_in.tg_id,
                                                           session)
        # TODO: Добавить проверку что оформляют пробную, если пользователь будет оформлять
        # TODO: например вторую подписку, то это правило не должно мешать ему это сделать
        if subscription:
            log_action_status(
                action_name='Наличие подписки!',
                message=f'Подписка уже есть у {user.telegram_id}'
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Подписка уже есть у пользователя!'
            )
        active_server = await self.check_active_server(data_in.protocol,
                                                       data_in.region_code,
                                                       session)
        device_count = {
            'trial': 1,
            '2_devices': 2,
            '4_devices': 4
        }.get(data_in.type, 1)
        # TODO: Будет универсальная ручка для всех протоколов, ответ разный
        cert_names = [uuid4().hex for _ in range(device_count)]
        log_action_status(
            action_name='Запрос пробной подписки',
            message=(f'Генерация {device_count} сертификатов '
                     f'для пользователя {user.telegram_id}')
        )
        cert_tasks = [
            self.request_certificate(active_server, name)
            for name in cert_names
        ]
        # cert_links: list[str] = await asyncio.gather(*cert_tasks)
        cert_links: list[str] = ['lol']
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
            type=subscription.type,
            end_date=subscription.end_date.date(),
            certificates=cert_links,
        )
        return subs_answer

    async def get_sub_with_cert(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> SubscriptionDB:
        user, subscription = await self.check_subscription(tg_id, session)
        subs_answer = SubscriptionDB(
            type=subscription.type,
            end_date=subscription.end_date.date(),
            certificates=[cert.filename for cert in subscription.certificates],
        )
        return subs_answer

    async def create_link_for_payment():
        pass


subscription_service = SubscriptionService()
