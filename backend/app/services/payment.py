import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError

from app.core.config import settings
from app.core.log_config import log_action_status
from app.core.variables import SettingServers
from app.crud.payment import payment_crud
from app.models.payment import PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdateStatus,
    YouKassaStatus,
    YooKassaWebhookNotification
)
from app.schemas.subscription import SubscriptionCreate


Configuration.account_id = settings.SHOP_ID
Configuration.secret_key = settings.SECRET_KEY_SHOP


async def create_payment(
    value: Decimal,
    data_in: SubscriptionCreate,
    user: User,
    session: AsyncSession,
) -> str:
    uuid_payment = uuid.uuid4()
    try:
        payment = Payment.create({
            'amount': {
                'value': value,
                'currency': SettingServers.DEFAULT_CURRENCY
            },
            'confirmation': {
                'type': SettingServers.DEFAULT_TYPE_CONFIRM,
                'return_url': SettingServers.URL_TGBOT
            },
            'capture': True,
            'description': f'Заказ клиента: {user.telegram_id}'
        }, uuid_payment)
    except ApiError as error:
            log_action_status(
                action_name='Формирование ссылки',
                message=('При формирования ссылки для пользователя: '
                         f'{user.telegram_id} произошла ошибка:{error}'),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка формировании ссылки, сообщите администратору.',
            )
    else:
        intent = {
            'sub_id': data_in.sub_id,
            "type": data_in.type,
            "duration": data_in.duration,
            "region_code": data_in.region_code if not data_in.sub_id else None,
            "protocol": data_in.protocol if not data_in.sub_id else None,
        }
        payment_db = PaymentCreate(
            amount=payment.amount.value,
            provider=SettingServers.YOOKASSA_NAME,
            status=PaymentStatus.pending,
            operation_id=payment.id,
            user_id=user.id,
            intent_data=intent
        )
        log_action_status(
            action_name='Формирование ссылки',
            message=('Успешное формирование ссылки для пользователя: '
                     f'{user.telegram_id} pay_id: {payment_db.operation_id}'),
        )
        await payment_crud.create(payment_db, session)
        return payment.confirmation.confirmation_url


async def check_status_from_yookassa(
    data_in: YooKassaWebhookNotification,
    session: AsyncSession,
):
    """Проверка статуса и присвоение рефералу бонуса."""
    # TODO: Реализовать логику начисления бонуса рефералу
    success = (True if data_in.object.status is YouKassaStatus.succeeded
               else False)
    if data_in.object.status is YouKassaStatus.waiting_for_capture:
        return None, False
    else:
        payment = await payment_crud.get_by_operation_id(
            data_in.object.id,
            session,
        )
        if payment.status is PaymentStatus.success:
            log_action_status(
                action_name='Оповещение о выполненной транзакции',
                message=(
                    f'Повторное уведомление по успешному платежу {payment.id} '
                    f'платеж уже был выполнен для юзера БД {payment.user_id}')
            )
            return None, False
        upd_status = PaymentUpdateStatus(status=data_in.object.status)
        payment = await payment_crud.update(payment, upd_status, session)
        return payment, success
