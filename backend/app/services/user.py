from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user_crud
from app.core.log_config import log_action_status, log_db_action
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """Логика действий с пользователями."""

    model = User
    crud = user_crud

    async def check_refer(
        self,
        refer_id: int,
        session: AsyncSession
    ) -> int | None:
        refer_user = await self.crud.get_by_tg_id(refer_id, session)
        if refer_user:
            return refer_user.id
        else:
            log_action_status(
                message=f'Предоставлен недействительный refer: {refer_id}')
            return None

    @log_db_action('Авторизация пользователя')
    async def get_or_create(
        self,
        user: UserCreate,
        session: AsyncSession
    ) -> User:
        user_from_db = await self.crud.get_by_tg_id(user.telegram_id, session)
        if user_from_db:
            return user_from_db
        if user.refer_from_id:
            user.refer_from_id = await self.check_refer(
                user.refer_from_id, session)
        new_user = await self.crud.create(user, session)
        return new_user


user_service = UserService()
