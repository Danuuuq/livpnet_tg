from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from app.models.payment import PaymentStatus
from app.models.server import VPNProtocol
from app.models.subscription import SubscriptionType, SubscriptionDuration


class PaymentCreate(BaseModel):
    """Схема для создания платежа."""

    amount: Decimal = Field(description='Стоимость услуги')
    provider: str = Field(description='Поставщик услуги')
    status: PaymentStatus = Field(description='Статус платежа')
    operation_id: str = Field(description='ID Операции')
    user_id: int = Field(description='ID пользователя')
    intent_data: dict | None = Field(
        default=None,
        description='Информация о подписке',
    )


class PaymentAnswer(BaseModel):
    """Схема для ответа с ссылкой на платеж."""

    amount: Decimal = Field(description='Стоимость услуги')
    type: SubscriptionType = Field(description='Количество устройств')
    duration: SubscriptionDuration = Field(
        description='Длительность подписки',
    )
    region_code: str = Field(
        min_length=2,
        max_length=2,
        description='Код региона (ISO)',
    )
    protocol: VPNProtocol = Field(description='Протокол VPN-соединения')
    url: str = Field(description='Ссылка на оплату')


class YouKassaStatus(str, Enum):
    waiting_for_capture = "waiting_for_capture"
    succeeded = "succeeded"
    canceled = "canceled"
    pending = "pending"


class YooKassaWebhookObject(BaseModel):
    id: str = Field(description="ID транзакции")
    status: YouKassaStatus = Field(description="Статус транзакции")


class YooKassaWebhookNotification(BaseModel):
    type: str = Field(description="Тип уведомления", example="notification")
    event: str = Field(description="Событие", example="payment.waiting_for_capture")
    object: YooKassaWebhookObject
