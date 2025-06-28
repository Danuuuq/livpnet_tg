from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

created_at = Annotated[datetime, mapped_column(
    server_default=func.now(timezone=True))]
updated_at = Annotated[datetime, mapped_column(
    server_default=func.now(timezone=True), onupdate=func.now(timezone=True))]


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для моделей."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
