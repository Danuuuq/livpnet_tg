from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.subscription import Subscription, SubscriptionPrice


class CRUDSubscription(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_user(self, user_id: int,
                          session: AsyncSession) -> Subscription | None:
        """Получение подписки пользователя."""
        db_obj = await session.execute(
            select(self.model)
            .options(selectinload(self.model.certificates))
            .where(self.model.user_id == user_id)
        )
        return db_obj.scalars().first()


subscription_crud = CRUDSubscription(Subscription)
price_crud = CRUDBase(SubscriptionPrice)
