import asyncio

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user_crud
from app.crud.server import server_crud
from app.crud.subscription import subscription_crud
from app.core.log_config import log_action_status
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate
from app.validators.base import get_or_404


class SubscriptionService:
    """Логика действий с пользователями."""

    model = Subscription
    crud = subscription_crud

    async def check_subscription(
        self,
        tg_id: int,
        session: AsyncSession,
    ) -> None:
        user = await user_crud.get_by_tg_id(tg_id, session)
        if user:
            return await subscription_crud.get_by_user(user.id, session)
        elif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден!'
            )

    async def request_certificate(
        url_server:str,
        name: str,
    ) -> StreamingResponse:
        """Отправка запроса на генерацию сертификата."""
        url = f"{url_server}/{settings.API_CERT_HOOK}/{name}"
        headers = {"Authorization": f"Bearer {settings.API_KEY}"}
        async with AsyncClient() as client:
            response = await client.post(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Ошибка запроса сертификата: {response.text}"
                )
        return response.content

    async def create_trial(
        self,
        data_in: SubscriptionCreate,
        session: AsyncSession,
    ) -> Subscription:
        # Проверяем что точно нет подписки
        if await self.check_subscription(data_in.tg_id, session):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Подписка уже есть у пользователя!'
            )
        # TODO: Получаем доступные сервера регион и протокол УЧЕСТЬ!:
        active_server = await server_crud.get_server_region_and_protocol(
            data_in.region_code, data_in.protocol, session)
        # Определяем количество устройств по типу подписки
        device_count = {
            'trial': 2,
            '2_devices': 2,
            '4_devices': 4
        }.get(data_in.type, 2)
        cert_names = [f'{data_in.tg_id}_{i}' for i in range(1, device_count + 1)]
        # TODO: Обращение к серверу по ip для получение vpn
        # TODO: Будет универсальная ручка для всех протоколов, ответ разный
        cert_tasks = [
            self.request_certificate(active_server.domain_name, name)
            for name in cert_names
        ]
        cert_contents: list[bytes] = await asyncio.gather(*cert_tasks)
        return None


subscription_service = SubscriptionService()
