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
    subscriptions = current_user.get('subscription')
    await message.answer(
        CommonMessage.format_start_message(
            name=message.from_user.first_name,
            main_menu=True,
            subscriptions=subscriptions,
        ),
        reply_markup=main_inline_kb()
    )


@router.callback_query(F.data == 'main_menu')
async def callback_start(call: CallbackQuery, state: FSMContext,
                         current_user: dict):
    """Возвращение в главное меню."""
    await state.clear()
    subscriptions = current_user.get('subscription')
    await call.message.delete()
    await call.message.answer(
        CommonMessage.format_start_message(
            name=call.from_user.first_name,
            main_menu=True,
            subscriptions=subscriptions,
        ),
        reply_markup=main_inline_kb()
    )
