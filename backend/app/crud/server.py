from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base import CRUDBase, CreateSchemaType
from app.core.database import commit_change
from app.models.server import Region, Server, Certificate
from app.schemas.subscription import CertificateCreateDB


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
        obj_in: dict,
        session: AsyncSession,
    ) -> Server:
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


class CRUDCertificate(CRUDBase):
    """CRUD операции для модели с сертификатами."""

    async def create(
        self,
        obj_in: CertificateCreateDB,
        session: AsyncSession,
    ) -> Certificate | None:
        """Создание объекта сертификата."""
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        server = await server_crud.get_by_id(obj_in.server_id, session)
        if server:
            server.current_cert_count += 1
            session.add(server)
        return await commit_change(session, db_obj)

    async def delete(
        self,
        db_obj: Certificate,
        session: AsyncSession,
    ) -> Certificate:
        """Удаление объекта модели."""
        server = await server_crud.get_by_id(db_obj.server_id, session)
        if server and server.current_cert_count > 0:
            server.current_cert_count -= 1
            session.add(server)
        await session.delete(db_obj)
        await commit_change(session)
        return db_obj


certificate_crud = CRUDCertificate(Certificate)
