import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.server import Certificate, Region
    from app.models.user import User


class SubscriptionType(str, enum.Enum):
    trial = "Пробная"
    devices_2 = "2 устройства"
    devices_4 = "4 устройства"


class SubscriptionDuration(str, enum.Enum):
    month_1 = "1 месяц"
    month_6 = "6 месяцев"
    year_1 = "1 год"


class Subscription(Base):
    """Модель для подписок."""

    type: Mapped[SubscriptionType] = mapped_column(
        Enum(SubscriptionType),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=SettingFieldDB.DEFAULT_ACTIVE_SUB,
        nullable=False,
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey('region.id'),
        nullable=True,
    )
    region: Mapped['Region'] = relationship(
        'Region',
        remote_side='Region.id',
        back_populates='subscriptions',
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False,
    )
    user: Mapped['User'] = relationship(
        'User',
        remote_side='User.id',
        back_populates='subscription',
    )
    certificates: Mapped[list['Certificate']] = relationship(
        'Certificate',
        back_populates='subscription',
        lazy='joined',
    )


class SubscriptionPrice(Base):
    """Цены на подписки."""

    type: Mapped[SubscriptionType] = mapped_column(
        Enum(SubscriptionType),
        nullable=False,
    )
    duration: Mapped[SubscriptionDuration] = mapped_column(
        Enum(SubscriptionDuration),
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    region_id: Mapped[int] = mapped_column(
        ForeignKey("region.id"),
        nullable=True,
    )
    __table_args__ = (
        UniqueConstraint("type", "duration", "region_id",
                         name="uniq_price_tariff"),
    )
