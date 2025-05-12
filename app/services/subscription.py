from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.server import server_crud
from app.crud.subscription import subscription_crud
from app.keyboards.inline import subscription_inline_kb
from app.messages.common import CommonMessage
from app.models.user import User


class SubscriptionService:
    """Класс сервиса для работы с Подписками."""

    crud = subscription_crud

    async def get_sub_user(
        self, user: User, call: CallbackQuery,
        session: AsyncSession) -> None:
        subscription = await self.crud.get_by_user(user.id, session)
        await call.message.delete()
        await call.message.answer(
            CommonMessage.SUBSCRIPTION_WELCOME,
            reply_markup=subscription_inline_kb(
                'trial' if not subscription else None))

    async def create_trial_sub(
        self, user: User, call: CallbackQuery,
        session: AsyncSession) -> None:
        if await self.crud.get_by_user(user.id, session):
            await call.message.delete()
            await call.message.answer(
                CommonMessage.BAD_CREATE_TRIAL_SUB,
                reply_markup=subscription_inline_kb())
        else:
            # Получить сервер у которого есть место для создания сертификатов
            await server_crud.get_active_servers(session)
            # Сделать запрос на создание сертификата
            # При успешном получение сертификата создать подписку
            # Далее создать объект модели сертификата с привязкой к подписке
            # Если сертификат не создался, то поменять сервер на другой, а тот
            # который вернул ошибку, изменить статус на неактивный (ДОП)
            # Повторить действия с другим сервером
            
        


subscription_service = SubscriptionService()
        
