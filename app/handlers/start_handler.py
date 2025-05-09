from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core.database import get_session_database
from app.crud.user import user_crud
from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage
from app.utils.utils import get_refer_id

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, command: CommandObject):
    """Команда для запуска/перезапуска бота у клиента."""
    await state.clear()
    async with get_session_database() as session:
        user = await user_crud.get_by_tg_id(message.from_user.id, session)
        if user:
            await message.answer(
                CommonMessage.HELLO_FOR_CLIENT.format(
                    name=user.name, user_id=user.telegram_id),
                reply_markup=main_inline_kb())
        else:
            refer_id = get_refer_id(command.args)
            if refer_id:
                refer_from = await user_crud.get_by_tg_id(refer_id, session)
                refer_from = refer_from.id
            else:
                refer_from = None
            new_user = {
                'telegram_id': message.from_user.id,
                'name': (message.from_user.first_name or
                         message.from_user.username),
                'refer_from_id': refer_from
            }
            user = await user_crud.create(new_user, session)
            await message.answer(CommonMessage.WELCOME.format(name=user.name),
                                 reply_markup=main_inline_kb())
