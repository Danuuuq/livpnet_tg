from fastapi import APIRouter

from app.api.rest import (
    server_router,
    subscription_router,
    user_router,
)

main_router = APIRouter()

main_router.include_router(
    user_router, prefix='/auth', tags=['Пользователи'])

main_router.include_router(
    server_router, prefix='/server', tags=['Сервера'])

main_router.include_router(
    subscription_router, prefix='/subscription', tags=['Подписки'])
