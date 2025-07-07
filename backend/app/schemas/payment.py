from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.core.variables import SettingFieldDB
from app.models.payment import PaymentStatus
from app.models.server import VPNProtocol
from app.models.subscription import SubscriptionType, SubscriptionDuration


class YouKassaStatus(str, Enum):
    waiting_for_capture = "waiting_for_capture"
    succeeded = "succeeded"
    canceled = "canceled"
    pending = "pending"

    def to_internal(self) -> PaymentStatus:
        return {
            YouKassaStatus.succeeded: PaymentStatus.success,
            YouKassaStatus.pending: PaymentStatus.pending,
            YouKassaStatus.canceled: PaymentStatus.failed,
        }[self]


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


class ReferralCreate(BaseModel):
    """Схема для создания бонуса для реферала."""

    user_id: int = Field(description='ID кому бонус за приглашение')
    invited_id: int = Field(description='ID кого пригласил')


class ReferralInviteInfo(BaseModel):
    """Схема по тому кого пригласил клиент."""

    invited_id: int = Field(description='ID приглашённого пользователя')
    bonus_given: bool = Field(description='Выплачен ли бонус')
    bonus_size: Decimal = Field(description='Размер бонуса')


class ReferralInfoOut(BaseModel):
    """Схема для всех начислений клиенту."""

    tg_id: int = Field(
        description='Телеграм ID пользователя (получателя бонусов)',
    )
    available_to_withdraw: Decimal = Field(
        description='Сумма, доступная к выводу (в рублях)'
    )
    available_user_count: int = Field(
        description='Количество приглашённых, за которых доступен бонус'
    )
    already_withdrawn: Decimal = Field(
        description='Сумма уже выведенных бонусов (в рублях)'
    )
    withdrawn_user_count: int = Field(
        description='Количество приглашённых, за которых бонус уже был выведен'
    )


class PaymentUpdateStatus(BaseModel):
    """Схема для создания платежа."""

    status: PaymentStatus = Field(description='Статус платежа')

    @field_validator('status', mode='before')
    def convert_yookassa_status(cls, v):
        try:
            return YouKassaStatus(v).to_internal()
        except ValueError:
            raise ValueError(f'Неверный статус оплаты: {v}')


class PaymentAnswer(BaseModel):
    """Схема для ответа с ссылкой на платеж."""

    amount: Decimal = Field(description='Стоимость услуги')
    type: SubscriptionType = Field(description='Количество устройств')
    duration: SubscriptionDuration = Field(
        description='Длительность подписки',
    )
    region_code: str = Field(
        min_length=SettingFieldDB.LENGTH_REGION_CODE,
        max_length=SettingFieldDB.LENGTH_REGION_CODE,
        description='Код региона (ISO)',
    )
    protocol: VPNProtocol | None = Field(
        default=None,
        description='Протокол VPN-соединения')
    url: str = Field(description='Ссылка на оплату')


class YooKassaWebhookObject(BaseModel):
    id: str = Field(description="ID транзакции")
    status: YouKassaStatus = Field(description="Статус транзакции")


class YooKassaWebhookNotification(BaseModel):
    type: str = Field(description="Тип уведомления", example="notification")
    event: str = Field(description="Событие", example="payment.waiting_for_capture")
    object: YooKassaWebhookObject
