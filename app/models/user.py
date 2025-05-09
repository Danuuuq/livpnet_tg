from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class User(Base):
    """Модель для пользователей."""

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_NAME), nullable=False)
    ref_count: Mapped[int] = mapped_column(
        Integer, default=SettingFieldDB.DEFAULT_FOR_COUNT, nullable=False)

    refer_from_id: Mapped[int | None] = mapped_column(
        ForeignKey('user.id'), nullable=True)
    refer_from: Mapped['User'] = relationship(
        'User', remote_side='User.id', back_populates='refer_to')

    refer_to: Mapped[list['User']] = relationship(
        'User', back_populates='refer_from')

    subscription: Mapped[list['Subscription']] = relationship(
        'Subscription', back_populates='user')
