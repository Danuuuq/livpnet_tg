from aiogram import Router, types
from aiogram.filters import Command

from app.services.certificates.generator import (
    generate_certificate,
    build_cert_name
)
from app.services.validators.sub_check import is_subscription_active
from app.crud.certificate import certificate_crud
from app.core.database import get_session_database
from enums import Message, Errors


router = Router()


@router.message(Command('get_cert'))
async def handle_get_cert(message: types.Message) -> None:
    user_id = message.from_user.id

    async with get_session_database() as db:
        is_active, sub = await is_subscription_active(user_id, db)
        if not is_active:
            await message.answer(Message.NOT_SUB)
            return
        cert_name = build_cert_name(user_id)
        try:
            path = generate_certificate(cert_name)
            await certificate_crud.save_certificate(
                db,
                filename=path.name,
                subscription_id=sub.id
            )
            await message.answer_document(types.FSInputFile(path))
        except Exception as e:
            await message.answer(Errors.BASE_ERROR.format(e=e))
