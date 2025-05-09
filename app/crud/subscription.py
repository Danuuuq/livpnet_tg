from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.subscription import Subscription


class CRUDSubscription(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_user(self, user_id: int,
                           session: AsyncSession) -> Subscription | None:
        """Получение объекта пользователя по id телеграмма."""
        db_obj = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return db_obj.scalars().first()


subscription_crud = CRUDSubscription(Subscription)
