from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, AsyncGenerator, TypeVar

from sqlalchemy import BigInteger, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings

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


engine = create_async_engine(settings.get_db_url)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)
ModelType = TypeVar('ModelType', bound=Base)


@asynccontextmanager
async def get_session_database() -> AsyncGenerator[AsyncSession, None]:
    """Создание сессий для подключения к БД."""
    async with async_session_maker() as async_session:
        try:
            yield async_session
        except SQLAlchemyError:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()


async def commit_change(
    session: AsyncSession,
    obj: ModelType | None = None) -> ModelType | None:
    """Безопасное выполнение действий с БД."""
    try:
        await session.commit()
        if obj:
            await session.refresh(obj)
    except (IntegrityError, SQLAlchemyError):
        await session.rollback()
        raise
    else:
        return obj
