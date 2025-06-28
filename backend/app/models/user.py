from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.payment import Payment, ReferralBonus
    from app.models.subscription import Subscription


class User(Base):
    """Модель для пользователей."""

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
    )
    ref_count: Mapped[int] = mapped_column(
        Integer,
        default=SettingFieldDB.DEFAULT_FOR_COUNT,
        nullable=False,
    )
    refer_from_id: Mapped[int | None] = mapped_column(
        ForeignKey('user.id'),
        nullable=True,
    )
    refer_from: Mapped['User'] = relationship(
        'User',
        remote_side='User.id',
        back_populates='refer_to',
    )
    refer_to: Mapped[list['User']] = relationship(
        'User',
        back_populates='refer_from',
    )
    subscription: Mapped[list['Subscription']] = relationship(
        'Subscription',
        back_populates='user',
        lazy='joined',
    )
    payments: Mapped[list['Payment']] = relationship(
        'Payment',
        back_populates='user',
        lazy='selectin',
    )
    invites: Mapped[list['ReferralBonus']] = relationship(
        'ReferralBonus',
        back_populates='invited',
        foreign_keys='ReferralBonus.invited_id',
        lazy='selectin',
    )
    referrals: Mapped[list['ReferralBonus']] = relationship(
        'ReferralBonus',
        back_populates='user',
        foreign_keys='ReferralBonus.user_id',
        lazy='selectin',
    )
