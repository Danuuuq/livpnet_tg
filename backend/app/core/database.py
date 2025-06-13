from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.core.log_config import log_action_status
from app.models.base import Base

engine = create_async_engine(settings.get_db_url)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)
ModelType = TypeVar('ModelType', bound=Base)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Создание сессий для подключения к БД."""
    async with async_session_maker() as async_session:
        try:
            log_action_status(message='Сессия открыта')
            yield async_session
        except SQLAlchemyError as e:
            await async_session.rollback()
            log_action_status(
                error=e,
                action_name='Ошибка работы с БД')
            raise SQLAlchemyError(f'Ошибка работы с БД: {str(e)}')
        finally:
            log_action_status(message='Сессия закрыта')
            await async_session.close()


@asynccontextmanager
async def get_session_database() -> AsyncGenerator[AsyncSession, None]:
    """Создание сессий для подключения к БД lifespan задач."""
    async for session in get_async_session():
        yield session


async def commit_change(
    session: AsyncSession,
    obj: ModelType | None = None,
) -> ModelType | None:
    """Безопасное выполнение действий с БД."""
    try:
        await session.commit()
        if obj:
            await session.refresh(obj)
    except SQLAlchemyError as e:
        await session.rollback()
        log_action_status(
            error=e,
            action_name='Сохранение в БД')
        raise SQLAlchemyError(f'Ошибка сохранения в БД: {str(e)}')
    else:
        return obj
