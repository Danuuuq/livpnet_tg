from aiogram.filters import CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user_crud
from app.keyboards.inline import main_inline_kb
from app.messages.common import CommonMessage
from app.models.user import User
from app.utils.utils import get_refer_id


class UserService:
    """Класс сервиса для работы с Юзерами."""

    crud = user_crud

    async def welcome_user(
        self, message: Message, user: User,
        command: CommandObject, session: AsyncSession) -> None:
        if user:
            await message.answer(
                CommonMessage.HELLO_FOR_CLIENT.format(
                    name=message.from_user.first_name),
                reply_markup=main_inline_kb())
        else:
            if command.args:
                refer_from = await self.check_refer_id(command.args, session)
            else:
                refer_from = None
            new_user = {
                'telegram_id': message.from_user.id,
                'refer_from_id': refer_from
            }
            user = await self.crud.create(new_user, session)
            await message.answer(CommonMessage.WELCOME.format(
                name=message.from_user.first_name),
                                 reply_markup=main_inline_kb())

    async def check_refer_id(self, ref_id: str, session: AsyncSession):
        refer_id = get_refer_id(ref_id)
        refer_from = await self.crud.get_by_tg_id(refer_id, session)
        if refer_from:
            return refer_from.id
        else:
            return None


user_service = UserService()
