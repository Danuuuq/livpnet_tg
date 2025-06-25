import enum

from pydantic import BaseModel, Field


class VPNProtocol(str, enum.Enum):
    openvpn = "OpenVPN"
    vless = "Vless"


class SubscriptionType(str, enum.Enum):
    trial = "Пробная"
    devices_2 = "2 устройства"
    devices_4 = "4 устройства"


class SubscriptionDuration(str, enum.Enum):
    month_1 = "1 месяц"
    month_6 = "6 месяцев"
    year_1 = "1 год"


class SubscriptionCreate(BaseModel):
    """Схема данных при оформлении подписки из Telegram."""

    tg_id: int = Field(description='Телеграмм id пользователя')
    sub_id: int | None = Field(default=None,
                               description='id подписки обновления')
    type: SubscriptionType = Field(description='Количество устройств')
    duration: SubscriptionDuration | None = Field(default=None,
                                                  description='Длительность подписки')
    region_code: str = Field(min_length=2, max_length=2,
                             description='Код региона (ISO)')
    protocol: VPNProtocol = Field(description='Протокол VPN-соединения')


class SubscriptionRenew(BaseModel):
    """Схема данных для продления подписки из Telegram."""

    tg_id: int = Field(description='Телеграмм id пользователя')
    sub_id: int = Field(description='id подписки обновления')
    extension: SubscriptionDuration = Field(description='Длительность подписки')


# class SubscriptionExtension(BaseModel):
#     """Схема данных при продлении подписки из Telegram."""

#     tg_id: int = Field(description='Телеграмм id пользователя')
#     sub_id: int = Field(description='id подписки обновления')
#     duration: SubscriptionDuration = Field(description='Длительность подписки')
