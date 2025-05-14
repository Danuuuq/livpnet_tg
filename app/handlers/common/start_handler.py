from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage
from app.models.user import User
from app.services.user import user_service

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, current_user: User,
    command: CommandObject, db_session: AsyncSession):
    """Команда для запуска бота и возврата в меню."""
    # Чистка состояния, если оно было вдруг
    await state.clear()
    await user_service.welcome_user(message, current_user, command, db_session)


@router.callback_query(F.data == '/start')
async def callback_start(call: CallbackQuery, state: FSMContext):
    """Кастомное решения для возвращения в start."""
    await call.message.delete()
    await call.message.answer(
        CommonMessage.HELLO_FOR_CLIENT.format(
            name=call.from_user.first_name),
        reply_markup=main_inline_kb())
