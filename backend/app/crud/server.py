from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.server import Region, Server, Certificate


class CRUDServer(CRUDBase):
    """CRUD операции для модели с подписками."""

    async def get_active_servers(
        self, session: AsyncSession) -> Sequence[Server] | None:
        """Получение объекта пользователя по id телеграмма."""
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.is_active)
            .options(joinedload(self.model.region))
        )
        return db_objs.scalars().all()

    async def get_region_by_code(
        self, code: str, session: AsyncSession) -> Region:
        db_obj = await session.execute(
            select(Region).where(Region.code == code)
        )
        return db_obj.scalars().first()

    async def get_server_from_region(
        self, code: str, session: AsyncSession) -> Sequence[Server] | None:
        """Получение объекта пользователя по id телеграмма."""
        region = await self.get_region_by_code(code, session)
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.is_active, self.model.region_id == region.id)
            .options(joinedload(self.model.region))
        )
        return db_objs.scalars().all()


server_crud = CRUDServer(Server)
certificate_crud = CRUDServer(Certificate)
