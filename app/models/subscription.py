from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.core.database import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.server import Certificate, Region
    from app.models.user import User


class Subscription(Base):
    """Модель для подписок."""

    type: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_TYPE_SUB), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=SettingFieldDB.DEFAULT_ACTIVE_SUB, nullable=False)

    region_id: Mapped[int] = mapped_column(
        ForeignKey('region.id'), nullable=True)
    region: Mapped['Region'] = relationship(
        'Region', remote_side='Region.id', back_populates='subscriptions')

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=True)
    user: Mapped['User'] = relationship(
        'User', remote_side='User.id', back_populates='subscription')

    certificates: Mapped[list['Certificate']] = relationship(
        'Certificate', back_populates='subscription', lazy='joined')
