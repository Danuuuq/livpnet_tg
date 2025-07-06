from fastapi import APIRouter

from app.api.broker import notify_router
from app.api.rest import (
    payment_router,
    server_router,
    subscription_router,
    user_router,
)

main_router = APIRouter()

main_router.include_router(
    user_router, prefix='/auth', tags=['Пользователи'])

main_router.include_router(
    notify_router, prefix='/notify', tags=['Уведомления и сообщения'])

main_router.include_router(
    payment_router, prefix='/payment', tags=['Платеж и рефералы'])

main_router.include_router(
    server_router, prefix='/server', tags=['Сервера'])

main_router.include_router(
    subscription_router, prefix='/subscription', tags=['Подписки'])
