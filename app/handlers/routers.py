from aiogram import Router

from .start_handler import router as start_router

main_router = Router()
main_router.include_router(start_router)
