from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers.routers import main_router
from app.middleware.user import UserMiddleware
from app.middleware.database import DBSessionMiddleware

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)

dp.message.middleware(DBSessionMiddleware())
dp.callback_query.middleware(DBSessionMiddleware())
dp.callback_query.middleware(UserMiddleware())
dp.message.middleware(UserMiddleware())
