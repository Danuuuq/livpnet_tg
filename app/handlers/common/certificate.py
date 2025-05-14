from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from app.services.certificates.user_cert import (
    get_user_certificate
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User


router = Router()


@router.callback_query(F.data == 'get_certificate')
async def handle_get_cert(
    call: CallbackQuery,
    db_session: AsyncSession,
    current_user: User
):
    """Команда для получения сертификата пользователем."""
    await call.answer('Получаю твой сертификат', show_alert=False)
    await get_user_certificate(current_user, call, db_session)
