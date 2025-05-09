from aiogram import Router

from app.handlers.common import start_router, subscription_router

main_router = Router()
main_router.include_routers(start_router, subscription_router)
