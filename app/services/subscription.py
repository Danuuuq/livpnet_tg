from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.server import server_crud, certificate_crud
from app.crud.subscription import subscription_crud
from app.forms.subscription import TrialSubForm
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

    async def check_available_sub(
        self, user: User, call: CallbackQuery,
        session: AsyncSession) -> None:
        if await self.crud.get_by_user(user.id, session):
            await call.message.delete()
            await call.message.answer(
                CommonMessage.BAD_CREATE_TRIAL_SUB,
                reply_markup=subscription_inline_kb())

    async def create_trial_sub(
        self, user: User, call: CallbackQuery,
        session: AsyncSession, state: TrialSubForm) -> None:
        # Получить сервер у которого есть место для создания сертификатов
        server = await server_crud.get_server_from_region(
            state.location, session)
        # server.ip_address(f'{user.telegram_id}_1') обращение к серверу за сертификатом
        # При успешном получение сертификата создать подписку
        subscription = {
            'type': 'trial',
            'is_active': True,
            'region_id': server.region_id,
            'user_id': user.id
        }
        subscription = await self.crud.create(subscription, session)
        # Далее создать объект модели сертификата с привязкой к подписке
        certificate = {
            'filename': f'{user.telegram_id}_1',
            'server_id': server.id,
            'subscription_id': subscription.id
        }
        certificate = await certificate_crud.create(certificate, session)
        # Если сертификат не создался, то поменять сервер на другой, а тот
        # который вернул ошибку, изменить статус на неактивный (ДОП)
        # Повторить действия с другим сервером
            
        


subscription_service = SubscriptionService()
        
