from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery, FSInputFile
from app.models import User
from app.services.certificates.generator import generate_certificate, build_cert_name
from app.crud.certificate import certificate_crud
from app.validators.sub_check import is_subscription_active
from enums import Messages, Errors


async def get_user_certificate(
    user: User,
    call: CallbackQuery,
    db_session: AsyncSession
):
    print('Проверка активной подписки')
    is_active, sub = await is_subscription_active(user.id, db_session)
    # if not is_active:
    #     await call.message.answer(Messages.NOT_SUB)
    #     return
    # print('Проверка активной подписки')
    cert_name = build_cert_name(user.id, 1)
    #, sub.id)
    print(cert_name, 'cert_name')
    # TODO тестируется без подписки, добавить сюда проверку подписки вместо 1

    try:
        # Генерация файла
        path = await generate_certificate(cert_name)
        print('path', path)
        # Сохранение в БД
        # await certificate_crud.create_certificate(
        #     session=db_session,
        #     filename=path.name,
        #     subscription_id=1
        # )

        # Отправка пользователю
        await call.message.answer_document(FSInputFile(path))
        await call.message.delete()
        await call.message.answer(Messages.TEST)

    except Exception as e:
        await call.message.answer(Errors.BASE_ERROR.format(e=e))
