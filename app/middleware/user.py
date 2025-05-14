from typing import Awaitable, Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.core.database import get_session_database
from app.crud.user import user_crud


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        async with get_session_database() as db_session:
            data['current_user'] = await user_crud.get_by_tg_id(
                event.from_user.id, db_session)
            return await handler(event, data)
