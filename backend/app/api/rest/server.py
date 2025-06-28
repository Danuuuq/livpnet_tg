from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.crud.server import server_crud
from app.services.server import server_service
from app.schemas.server import (
    ServerWithRegionDB,
    ServerDB,
    ServerCreate,
    ServerUpdate,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[ServerWithRegionDB],
    summary='Информация о всех серверах',
    response_description='Информация о всех серверах',
)
async def get_all_server(
    session: AsyncSession = Depends(get_async_session),
) -> list[ServerWithRegionDB]:
    """Выдача информации о всех серверах."""
    return await server_crud.get_all(session)


@router.get(
    '/active',
    response_model=list[ServerWithRegionDB],
    summary='Информация о доступных серверах',
    response_description='Предоставление доступных серверов',
)
async def get_active_server(
    session: AsyncSession = Depends(get_async_session),
) -> list[ServerWithRegionDB]:
    """Выдача всех активных(свободных) серверов."""
    return await server_crud.get_active_servers(session)


@router.post(
    '/',
    response_model=ServerDB,
    status_code=status.HTTP_201_CREATED,
    summary='Добавление нового сервера',
    response_description='Добавление нового сервера',
)
async def create_new_server(
    server: ServerCreate,
    session: AsyncSession = Depends(get_async_session),
) -> ServerDB:
    """Добавление нового сервера в БД."""
    # TODO: Новый сервер будет делать сюда запрос
    # TODO: чтобы добавить информацию о себе
    return await server_service.create(server, session)


@router.delete(
    '/{server_id}',
    response_model=ServerDB,
    summary='Удаление информации о сервере',
    response_description='Удаление информации о сервере',
)
async def delete_server(
    server_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ServerDB:
    """Удаление сервера из БД."""
    return await server_service.delete(server_id, session)


@router.patch(
    '/{server_id}',
    response_model=ServerDB,
    summary='Обновление информации о сервере',
    response_description='Обновление информации о сервере',
)
async def update_post(
    server_id: int,
    obj_in: ServerUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> ServerDB:
    """Редактирование поста."""
    server = await server_crud.get_by_id(server_id, session)
    return await server_crud.update(server, obj_in, session)
