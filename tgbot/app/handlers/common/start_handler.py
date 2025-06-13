from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, current_user: dict):
    """Команда для запуска бота."""
    await state.clear()
    subscription = current_user.get('subscription')
    if subscription:
        await message.answer(
            CommonMessage.HELLO_FOR_CLIENT.format(
                name=message.from_user.first_name,
                end_data=subscription.get('end_date')),
            reply_markup=main_inline_kb())
    else:
        await message.answer(
            CommonMessage.HELLO_WITHOUT_SUB.format(
                name=message.from_user.first_name),
            reply_markup=main_inline_kb())


@router.callback_query(F.data == 'main_menu')
async def callback_start(call: CallbackQuery, state: FSMContext,
                         current_user: dict):
    """Возвращение в главное меню."""
    await state.clear()
    subscription = current_user.get('subscription')
    if subscription:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.HELLO_FOR_CLIENT.format(
                name=call.from_user.first_name,
                end_data=subscription.get('end_date')),
            reply_markup=main_inline_kb())
    else:
        await call.message.delete()
        await call.message.answer(
            CommonMessage.HELLO_WITHOUT_SUB.format(
                name=call.from_user.first_name),
            reply_markup=main_inline_kb())
