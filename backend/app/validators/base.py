from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.base import Base


async def get_or_404(
    crud: CRUDBase,
    obj_id: int,
    session: AsyncSession
) -> Base:
    """Проверка на наличие объекта в базе данных."""
    db_obj = await crud.get_by_id(obj_id, session)
    if db_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Объект с id: {obj_id} отсутствует'
        )
    return db_obj
