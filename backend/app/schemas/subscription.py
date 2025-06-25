from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.server import VPNProtocol
from app.models.subscription import SubscriptionType, SubscriptionDuration


class CertificateFile(BaseModel):
    """Информация о сертификате."""

    filename: str = Field(description='Имя файла сертификата')
    url_vless: str | None = Field(description='Ссылка на подключение')


class PriceDB(BaseModel):
    """Базовая модель для регионов."""

    type: str = Field(description='Количество устройств')
    duration: str = Field(description='Длительность подписки')
    price: Decimal = Field(description='Цена подписки')

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    """Схема данных при оформлении подписки из Telegram."""

    tg_id: int = Field(description='Телеграмм id пользователя')
    sub_id: int | None = Field(default=None,
                               description='Id подписки при обновлении')
    type: SubscriptionType = Field(description='Количество устройств')
    duration: SubscriptionDuration | None = Field(default=None,
                                                  description='Длительность подписки')
    region_code: str = Field(min_length=2, max_length=2,
                             description='Код региона (ISO)')
    protocol: VPNProtocol = Field(description='Протокол VPN-соединения')

    @model_validator(mode='after')
    def validate_duration_for_type(self) -> 'SubscriptionCreate':
        if self.type != SubscriptionType.trial and self.duration is None:
            raise ValueError(
                'Для платной подписки параметр duration обязателен.'
            )
        if self.type == SubscriptionType.trial and self.duration is not None:
            raise ValueError(
                'Для пробной подписки параметр duration не должен быть указан.'
            )
        return self


class SubscriptionRenew(BaseModel):
    """Схема данных при оформлении подписки из Telegram."""

    tg_id: int = Field(description='Телеграмм id пользователя')
    sub_id: int = Field(description='id подписки обновления')
    extension: SubscriptionDuration = Field(description='Длительность подписки')


class RegionShort(BaseModel):
    code: str = Field(description='Код региона (ISO)')
    name: str = Field(description='Название региона')

    model_config = ConfigDict(from_attributes=True)


class SubscriptionInfoShortDB(BaseModel):
    """Информация о подписке пользователя."""


    id: int = Field(description='ID подписки')
    type: SubscriptionType = Field(
        description='Тип подписки: количество устройств')
    end_date: datetime = Field(description='Дата окончания')

    model_config = ConfigDict(from_attributes=True)


class SubscriptionInfoDB(SubscriptionInfoShortDB):
    """Информация о подписке пользователя."""

    region: RegionShort = Field(description='Регион подписки')


class SubscriptionDB(SubscriptionInfoDB):
    """Подробная информация о подписке пользователя."""
    certificates: list[str] = Field(
        description='Ссылки на загрузку сертификатов')


class SubscriptionCreateDB(BaseModel):
    """Схема для создания подписки в БД."""

    user_id: int = Field(description='ID пользователя')
    region_id: int = Field(description='ID региона')
    type: SubscriptionType = Field(description='Тип подписки')
    is_active: bool = Field(default=True, description='Активна ли подписка')
    end_date: datetime = Field(description='Дата окончания подписки')


class CertificateCreateDB(BaseModel):
    """Схема для создания сертификата в БД."""

    filename: str = Field(description='Имя файла сертификата')
    url_vless: str | None = Field(default=None,
                                  description='Ссылка на vless (если есть)')
    server_id: int = Field(description='ID сервера')
    subscription_id: int = Field(description='ID подписки')
