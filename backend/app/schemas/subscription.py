from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.server import VPNProtocol
from app.models.subscription import SubscriptionType, SubscriptionDuration


class CertificateFile(BaseModel):
    """Информация о сертификате."""

    filename: str = Field(description="Имя файла сертификата")
    url_vless: str | None = Field(description="Ссылка на подключение")


class PriceDB(BaseModel):
    """Базовая модель для регионов."""

    type: str = Field(description='Количество устройств')
    duration: str = Field(description='Длительность подписки')
    price: int = Field(description='Цена подписки')

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    """Схема данных при оформлении подписки из Telegram."""

    tg_id: int = Field(description='Телеграмм id пользователя')
    type: SubscriptionType = Field(description='Количество устройств')
    duration: SubscriptionDuration = Field(description='Длительность подписки')
    region_code: str = Field(min_length=2, max_length=2,
                             description='Код региона (ISO)')
    protocol: VPNProtocol = Field(description='Протокол VPN-соединения')


class SubscriptionDB(BaseModel):
    """Подробная информация о подписке пользователя."""

    type: SubscriptionType = Field(description="Тип подписки: количество устройств")
    end_date: datetime = Field(description="Дата окончания")
    certificates: list[CertificateFile] = Field(description="Список сертификатов")
