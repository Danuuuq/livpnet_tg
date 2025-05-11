from typing import Awaitable, Callable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.core.database import get_session_database


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        async with get_session_database() as db_session:
            data['db_session'] = db_session
            return await handler(event, data)
