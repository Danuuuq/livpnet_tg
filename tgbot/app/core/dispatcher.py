from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers.routers import main_router
from app.middleware.user import UserMiddleware

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)

dp.callback_query.middleware(UserMiddleware())
dp.message.middleware(UserMiddleware())
