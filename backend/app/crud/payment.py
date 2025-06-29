from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.payment import Payment, PaymentStatus, ReferralBonus
from app.models.user import User


class CRUDPayment(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_operation_id(
        self,
        operation_id: int,
        session: AsyncSession,
    ) -> Payment:
        """Получение объекта оплаты по id транзакции."""
        result = await session.execute(
            select(self.model)
            .options(
                joinedload(self.model.user)
                .joinedload(User.invites))
            .where(self.model.operation_id == operation_id)
        )
        return result.scalars().first()

    async def get_by_success_user(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> list[Payment] | None:
        """Получение успешных платежей пользователя."""
        db_obj = await session.execute(
            select(self.model)
            .where(self.model.user_id == user_id,
                   self.model.status == PaymentStatus.success)
        )
        return db_obj.scalars().all()


class CRUDReferral(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_invite(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> ReferralBonus | None:
        """Получение информации о начислении бонуса за клиента."""
        db_obj = await session.execute(
            select(self.model)
            .where(self.model.invited_id == user_id)
        )
        return db_obj.scalars().first()

    async def get_by_user(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> list[ReferralBonus] | None:
        """Получение информации о бонусах клиента."""
        db_obj = await session.execute(
            select(self.model)
            .where(self.model.user_id == user_id)
        )
        return db_obj.scalars().all()


payment_crud = CRUDPayment(Payment)
referral_crud = CRUDReferral(ReferralBonus)
