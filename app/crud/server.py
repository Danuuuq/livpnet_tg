from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.server import Server


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


server_crud = CRUDServer(Server)
