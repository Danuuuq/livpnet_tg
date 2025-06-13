from typing import Awaitable, Callable, Dict, Any

import aiohttp
from aiogram import BaseMiddleware
from aiogram.types import Message

from app.core.config import settings
from app.schemas.user import UserBase


class UserMiddleware(BaseMiddleware):

    async def fetch_user_data(self, event):
        refer_from = None
        if (isinstance(event, Message) and
            event.text and event.text.startswith("/start")):
            arg_ref = event.text.strip().split(maxsplit=1)
            refer_from = int(arg_ref[1]) if (len(arg_ref) > 1 and
                                             arg_ref[1].isdigit()) else None
        payload = UserBase(telegram_id=event.from_user.id,
                           refer_from_id=refer_from)
        url = settings.get_backend_url + settings.AUTH_PATH
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload.model_dump()) as resp:
                if resp.status != 201:
                    return {}
                return await resp.json()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        user_data = await self.fetch_user_data(event)
        data['current_user'] = user_data
        return await handler(event, data)
