from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.payment import Payment, ReferralBonus


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
            .options(joinedload(self.model.user))
            .where(self.model.operation_id == operation_id)
        )
        return result.scalars().first()


payment_crud = CRUDPayment(Payment)
referral_crud = CRUDBase(ReferralBonus)
