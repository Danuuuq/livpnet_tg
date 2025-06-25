from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.server import server_crud
from app.core.log_config import log_action_status
from app.models.server import Server
from app.schemas.server import ServerCreate
from app.validators.base import get_or_404


class ServerService:
    """Логика действий с пользователями."""

    model = Server
    crud = server_crud

    async def create(
        self,
        obj_in: ServerCreate,
        session: AsyncSession,
    ) -> Server:
        data = obj_in.model_dump()

        region_code = data.pop('region_code', None)
        if region_code is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Регион необходимо указать.'
            )
        elif region_code:
            region = await self.crud.get_region_by_code(region_code, session)
            if not region:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Регион с кодом "{region_code}" не найден.'
                )
            data['region_id'] = region.id

        return await self.crud.create(data, session)

    async def delete(
        self,
        server_id: int,
        session: AsyncSession,
    ) -> Server:
        """Удаление поста."""
        server = await get_or_404(self.crud, server_id, session)
        log_action_status(
            message=f'Удаление {server.ip_address}')
        return await self.crud.delete(server, session)


server_service = ServerService()
