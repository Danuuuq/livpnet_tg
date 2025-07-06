from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.crud.subscription import price_crud
from app.schemas.payment import PaymentAnswer, YooKassaWebhookNotification
from app.schemas.subscription import (
    PriceDB,
    SubscriptionDB,
    SubscriptionCreate,
    SubscriptionRenew,
)
from app.services.payment import check_status_from_yookassa
from app.services.subscription import subscription_service

router = APIRouter()


@router.get(
    '/price',
    response_model=list[PriceDB],
    summary='Информация о ценах на подписки',
    response_description='Информация о вариантах подписок',
)
async def get_all_price(
    session: AsyncSession = Depends(get_async_session),
) -> list[PriceDB]:
    """Выдача информации о ценах на подписки."""
    return await price_crud.get_all(session)


@router.post(
    '/',
    response_model=SubscriptionDB | PaymentAnswer,
    responses={
        200: {
            "description": "Ссылка на оплату",
            "model": PaymentAnswer,
        },
        201: {
            "description": "Пробная подписка оформлена",
            "model": SubscriptionDB,
        },
    },
    summary='Пробная подписка или оплата',
    response_description='Создание пробной подписки или ссылки на оплату',
)
async def create_subscription(
    data_in: SubscriptionCreate | SubscriptionRenew,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse | PaymentAnswer:
    """Оформление подписки для пользователя."""
    result = await subscription_service.trial_or_payment(data_in, session)
    if isinstance(result, SubscriptionDB):
        return JSONResponse(
            status_code=201,
            content=result.model_dump(mode='json'),
        )
    return result


@router.post(
    '/answer',
    summary='Webhook для ю.кассы',
    response_description='Ожидание ответа от ю.кассы об оплате.',
)
async def webhook_payment_status(
    data_in: YooKassaWebhookNotification,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Действия после выполнения или не выполнения оплаты."""
    payment, success = await check_status_from_yookassa(data_in, session)
    if success:
        await subscription_service.action_after_payment(payment, session)


# @router.delete(
#     '',
#     summary='Деактивация подписок и уведомление клиентов',
#     response_description=(
#         'Деактивация неоплаченных подписок и уведомление клиентов'
#         ' об окончании скорейшем.'),
# )
# async def delete_subscriptions(
#     session: AsyncSession = Depends(get_async_session),
# ):
#     """Деактивация подписок и уведомление об окончании."""
#     return await subscription_service.notify_about_subs(session)


@router.get(
    '/{tg_id}',
    response_model=list[SubscriptionDB],
    summary='Подписки пользователя',
    response_description='Выдать пользователю подписки с сертификатами',
)
async def get_subscriptions(
    tg_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> list[SubscriptionDB]:
    """Выдача информации о подписках и сертификатах."""
    return await subscription_service.get_sub_with_cert(tg_id, session)


@router.patch(
    '/',
    response_model=PaymentAnswer,
    summary='Обновление|продление подписки пользователя',
    response_description='Изменение или продление подписки',
)
async def update_subscription(
    data_in: SubscriptionRenew,
    session: AsyncSession = Depends(get_async_session),
) -> PaymentAnswer:
    """Обновление или продление подписки."""
    return await subscription_service.pay_update_subscription(
        data_in,
        session,
    )


# @router.delete(
#     '/{tg_id}/{sub_id}',
#     response_model=SubscriptionDB,
#     summary='Удаление сертификатов подписки пользователя',
#     response_description='Удаление сертификатов пользователя',
# )
# async def delete_subs_user(
#     tg_id: int,
#     sub_id: int,
#     session: AsyncSession = Depends(get_async_session),
# ) -> SubscriptionDB:
#     """Удаление/аннулирование сертификатов пользователя."""
#     return await subscription_service.revoke_certificate(
#         tg_id,
#         sub_id,
#         session,
#     )
