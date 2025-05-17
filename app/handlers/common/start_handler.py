from aiogram import F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage
from app.models.user import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext,
                    current_user: User, command: CommandObject):
    """Команда для запуска бота и возврата в меню."""
    await state.clear()
    if current_user:
        await message.answer(
            CommonMessage.HELLO_FOR_CLIENT.format(
                name=message.from_user.first_name),
            reply_markup=main_inline_kb())
    else:
        # TODO: Передаем бэкенду информацию о клиенте
        # TODO: и аргументы команды для рефералки
        # TODO: command & message.from_user
        await message.answer(
            CommonMessage.WELCOME.format(
                name=message.from_user.first_name),
            reply_markup=main_inline_kb())


@router.callback_query(F.data == 'main_menu')
async def callback_start(call: CallbackQuery, state: FSMContext):
    """Возвращение в главное меню."""
    await state.clear()
    await call.message.delete()
    await call.message.answer(
        CommonMessage.HELLO_FOR_CLIENT.format(
            name=call.from_user.first_name),
        reply_markup=main_inline_kb())
