from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.payment import ReferralInfoOut
from app.services.payment import get_bonus_info

router = APIRouter()


@router.get(
    '/{tg_id}',
    response_model=ReferralInfoOut,
    summary='Информация о бонусах',
    response_description='Выдача информации о бонусах пользователя',
)
async def get_info_bonus(
    tg_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ReferralInfoOut:
    """Информация о количестве бонусов клиента"""
    return await get_bonus_info(tg_id, session)
