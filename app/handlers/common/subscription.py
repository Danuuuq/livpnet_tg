from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.bot import bot
from app.crud.server import server_crud
from app.forms.subscription import TrialSubForm
from app.keyboards.inline import chose_location_server_kb
from app.messages.common import CommonMessage
from app.models.user import User
from app.services.subscription import subscription_service

router = Router()


@router.callback_query(F.data == 'get_subscription')
async def get_subscription_user(call: CallbackQuery, db_session: AsyncSession,
                                current_user: User):
    """CallBack запрос для получения подписки пользователя."""
    await call.answer('Загружаю информацию о подписке', show_alert=False)
    await subscription_service.get_sub_user(current_user, call, db_session)


@router.callback_query(F.data == 'get_trial')
async def get_trial(call: CallbackQuery, db_session: AsyncSession,
                    current_user: User, state: FSMContext):
    """CallBack запрос для получения пробной подписки."""
    await state.clear()
    await call.answer('Начинаем оформление подписки', show_alert=False)
    await subscription_service.check_available_sub(
        current_user, call, db_session)
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        servers = await server_crud.get_active_servers(db_session)
        await call.message.delete()
        await call.message.answer(
            'Выбери локацию для подключения',
            reply_markup=chose_location_server_kb(servers))
    await state.set_state(TrialSubForm.location)


@router.callback_query(F.data, TrialSubForm.location)
async def create_trial_subscription(
    call: CallbackQuery, db_session: AsyncSession,
    current_user: User, state: FSMContext):
    await subscription_service.create_trial_sub(current_user, call, 
                                                db_session, state)
    await state.clear()