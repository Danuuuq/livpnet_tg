import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.user import User


class PaymentStatus(str, enum.Enum):
    success = 'Успешно'
    pending = 'Ожидание'
    failed = 'Ошибка'


class Payment(Base):
    """Модель для платежей."""

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_NAME_PROVIDER), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False)
    operation_id: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_ID_OPERATION),
        nullable=False, unique=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False)
    user: Mapped['User'] = relationship(
        'User', remote_side='User.id', back_populates='payments')


class ReferralBonus(Base):
    """Модель для реферальных ссылок."""

    bonus_given: Mapped[bool] = mapped_column(
        Boolean, default=SettingFieldDB.DEFAULT_GIVEN_BONUS, nullable=False)

    bonus_size: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=SettingFieldDB.DEFAULT_BONUS, nullable=False)

    invited_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False)
    invited: Mapped['User'] = relationship(
        'User', remote_side='User.id', back_populates='invites')

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=False)
    user: Mapped['User'] = relationship(
        'User', remote_side='User.id', back_populates='referrals')

    __table_args__ = (
        UniqueConstraint('user_id', 'invited_id', name='uq_user_invited'),
    )
