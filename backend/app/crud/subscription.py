from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.server import Certificate
from app.models.subscription import Subscription, SubscriptionPrice
from app.schemas.subscription import SubscriptionDuration, SubscriptionType


class CRUDSubscription(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_id(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Subscription | None:
        """Получение подписки по id со всеми данными."""
        db_obj = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.certificates)
                .selectinload(Certificate.server),
                selectinload(self.model.region))
            .where(self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_by_user(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> Subscription | None:
        """Получение подписки пользователя."""
        db_obj = await session.execute(
            select(self.model)
            .options(selectinload(self.model.certificates))
            .where(self.model.user_id == user_id)
        )
        return db_obj.scalars().first()

    async def get_expired_subs(
        self,
        session: AsyncSession,
    ) -> list[Subscription]:
        """Получить подписки, которые уже истекли, но все еще активны."""
        today = datetime.now(timezone.utc).date()

        db_obj = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.certificates),
                selectinload(self.model.user),
                selectinload(self.model.region))
            .where(
                self.model.end_date < today,
                self.model.is_active.is_(True),
            )
        )
        return db_obj.unique().scalars().all()

    async def get_expiring_subs(
        self,
        session: AsyncSession,
    ) -> list[Subscription]:
        """Получить подписки, срок которых истекает завтра."""
        today = datetime.now(timezone.utc).date()

        db_obj = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.region))
            .where(
                func.date(self.model.end_date) == today,
                self.model.is_active.is_(True),
            )
        )
        return db_obj.unique().scalars().all()


class CRUDPrice(CRUDBase):
    """CRUD операции для модели с ценами."""

    async def get_by_type_and_duration(
        self,
        sub_duration: SubscriptionDuration,
        sub_type: SubscriptionType,
        session: AsyncSession,
    ) -> SubscriptionPrice | None:
        """Получение подписки пользователя."""
        db_obj = await session.execute(
            select(self.model.price)
            .where(
                self.model.duration == sub_duration,
                self.model.type == sub_type)
        )
        return db_obj.scalars().first()


subscription_crud = CRUDSubscription(Subscription)
price_crud = CRUDPrice(SubscriptionPrice)
