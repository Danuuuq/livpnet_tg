from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.core.database import get_session_database
from app.crud.user import user_crud
from app.crud.subscription import subscription_crud
from app.messages.common import CommonMessage
from app.keyboards.inline import subscription_inline_kb

router = Router()


@router.callback_query(F.data == 'get_subscription')
async def get_subscription_user(call: CallbackQuery):
    """CallBack запрос для получения подписки пользователя."""
    await call.answer('Загружаю информацию о подписке', show_alert=False)
    async with get_session_database() as session:
        user = await user_crud.get_by_tg_id(call.from_user.id, session)
        subscription = await subscription_crud.get_by_user(user.id, session)
        if not subscription:
            await call.message.delete()
            await call.message.answer(CommonMessage.SUBSCRIPTION_WELCOME,
                                      reply_markup=subscription_inline_kb('trial'))
