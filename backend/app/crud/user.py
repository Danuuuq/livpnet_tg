from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase):
    """CRUD операции для модели с пользователями."""

    async def get_by_tg_id(self, tg_id: int,
                           session: AsyncSession) -> User | None:
        """Получение объекта пользователя по id телеграмма."""
        db_obj = await session.execute(
            select(self.model).where(self.model.telegram_id == tg_id)
        )
        return db_obj.scalars().first()


user_crud = CRUDUser(User)
