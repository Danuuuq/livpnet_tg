from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.crud.subscription import subscription_crud, price_crud
from app.schemas.subscription import PriceDB

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
    """Выдача информации о всех серверах."""
    return await price_crud.get_all(session)