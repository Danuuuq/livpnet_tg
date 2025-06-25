from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.user import UserCreate, UserDB
from app.services.user import user_service

router = APIRouter()


@router.post(
    '/',
    response_model=UserDB,
    status_code=status.HTTP_201_CREATED,
    summary='Авторизация пользователя',
    response_description='Успешная авторизация пользователя',
)
async def register_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session),
) -> UserDB:
    """Авторизация пользователя в боте при входе в меню.

    - **telegram_id** — телеграм id пользователя;
    - **refer_from_id** — id (в БД) пользователя который пригласил;
    Возвращает созданного пользователя с метаинформацией.
    """
    user = await user_service.get_or_create(user, session)
    return UserDB.model_validate(user)
