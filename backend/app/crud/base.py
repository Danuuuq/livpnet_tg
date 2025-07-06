from typing import Generic, Type, TypeVar, Sequence

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import commit_change
from app.models.base import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[CreateSchemaType, UpdateSchemaType, ModelType]):
    """Базовые CRUD операции."""

    def __init__(
        self,
        model: Type[ModelType],
    ) -> None:
        """Инициализация модели для CRUD операций."""
        self.model = model

    async def get_by_id(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> ModelType | None:
        """Получение объекта модели по id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_all(
        self,
        session: AsyncSession,
    ) -> Sequence[ModelType]:
        """Получить все объекты модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
    ) -> ModelType | None:
        """Создание объекта модели."""
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        return await commit_change(session, db_obj)

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType | None:
        """Обновление объекта модели."""
        update_data = obj_in.model_dump(exclude_unset=True)
        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        return await commit_change(session, db_obj)

    async def delete(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType | None:
        """Удаление объекта модели."""
        await session.delete(db_obj)
        await commit_change(session)
        return db_obj
