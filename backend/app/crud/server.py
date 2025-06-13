from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base import CRUDBase
from app.core.database import commit_change
from app.models.server import Region, Server, Certificate
from app.schemas.server import ServerCreate


class CRUDServer(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_by_id(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Server:
        """Получение объекта модели по id."""
        result = await session.execute(
            select(self.model)
            .options(selectinload(self.model.region))
            .where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def get_all(
        self,
        session: AsyncSession,
    ) -> Sequence[Server]:
        """Получить все объекты модели."""
        result = await session.execute(
            select(self.model)
            .options(selectinload(self.model.region))
        )
        return result.scalars().all()

    async def create(
        self,
        obj_in: ServerCreate,
        session: AsyncSession,
    ) -> Server:
        # data = obj_in.model_dump()

        # region_code = data.pop("region_code", None)
        # if region_code:
        #     region = await self.get_region_by_code(region_code, session)
        #     if not region:
        #         raise ValueError(f"Регион с кодом '{region_code}' не найден.")
        #     data["region_id"] = region.id

        db_obj = self.model(**obj_in)
        session.add(db_obj)
        return await commit_change(session, db_obj)

    async def get_active_servers(
        self,
        session: AsyncSession,
    ) -> Sequence[Server] | None:
        """Получение активных серверов."""
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.is_active)
            .options(joinedload(self.model.region))
        )
        return db_objs.scalars().all()

    async def get_region_by_code(
        self,
        code: str,
        session: AsyncSession,
    ) -> Region:
        """Получение региона по коду."""
        db_obj = await session.execute(
            select(Region).where(Region.code == code)
        )
        return db_obj.scalars().first()

    async def get_server_region_and_protocol(
        self,
        code: str,
        protocol: str,
        session: AsyncSession,
    ) -> Sequence[Server] | None:
        """Получение серверов из определенного региона."""
        region = await self.get_region_by_code(code, session)
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.is_active,
                   self.model.region_id == region.id,
                   self.model.protocol == protocol)
            .options(joinedload(self.model.region))
        )
        return db_objs.scalars().all()


server_crud = CRUDServer(Server)
certificate_crud = CRUDServer(Certificate)
