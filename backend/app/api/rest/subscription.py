from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.crud.subscription import subscription_crud, price_crud
from app.schemas.subscription import PriceDB, SubscriptionDB, SubscriptionCreate
from app.services.subscription import subscription_service

router = APIRouter()


@router.get(
    '/price',
    response_model=list[PriceDB],
    summary='Информация о ценах на подписки',
    response_description='Информация о вариантах подписок',
)
async def get_all_price(
    session: AsyncSession = Depends(get_async_session),
) -> list[PriceDB]:
    """Выдача информации о ценах на подписки."""
    return await price_crud.get_all(session)


@router.post(
    '/',
    response_model=SubscriptionDB,
    summary='Создание первой подписки',
    response_description='Создание первой/пробной подписки',
)
async def create_subscription(
    data_in: SubscriptionCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SubscriptionDB:
    """Выдача информации о всех серверах."""
    return await subscription_service.create(data_in, session)


@router.get(
    '/{tg_id}',
    response_model=SubscriptionDB,
    summary='Подписка пользователя',
    response_description='Выдать пользователю подписку с сертификатами',
)
async def get_subscription(
    tg_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> SubscriptionDB:
    """Выдача информации о всех серверах."""
    return await subscription_service.get_sub_with_cert(tg_id, session)
