from typing import Generic, Type, TypeVar, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, commit_change

ModelType = TypeVar('ModelType', bound=Base)
DictType = TypeVar('DictType', bound=dict)


class CRUDBase(Generic[DictType, ModelType]):
    """Базовые CRUD операции."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализация модели для CRUD операций."""
        self.model = model

    async def get_by_id(self, obj_id: int,
                        session: AsyncSession) -> ModelType | None:
        """Получение объекта модели по id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_all(self, session: AsyncSession) -> Sequence[ModelType]:
        """Получить все объекты модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(self, obj_in: DictType,
                     session: AsyncSession) -> ModelType | None:
        """Создание объекта модели."""
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        return await commit_change(session, db_obj)

    async def update(self, db_obj: ModelType, obj_in: DictType,
                     session: AsyncSession) -> ModelType | None:
        """Обновление объекта модели."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        return await commit_change(session, db_obj)

    async def delete(self, db_obj: ModelType,
                     session: AsyncSession) -> ModelType | None:
        """Удаление объекта модели."""
        await session.delete(db_obj)
        await commit_change(session)
        return db_obj
