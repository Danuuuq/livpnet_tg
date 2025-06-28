from ipaddress import ip_address
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from app.models.server import VPNProtocol


class RegionBase(BaseModel):
    """Базовая модель для регионов."""

    code: str = Field(description='Код региона (ISO)')
    name: str = Field(description='Название региона')


class RegionDB(RegionBase):
    """Модель для выдачи информации и регионе."""

    model_config = ConfigDict(from_attributes=True)


class ServerBase(BaseModel):
    """Базовая схема данных серверов."""

    ip_address: str | None = Field(default=None,
                                   description='IP-адрес сервера')
    domain_name: str | None = Field(default=None,
                                    description='Доменное имя')
    protocol: VPNProtocol | None = Field(default=None,
                                         description='Протокол работы сервера')
    is_active: bool | None = Field(default=None,
                                   description='Доступность сервера')

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            ip_address(v)
        except ValueError:
            raise ValueError('Неверный формат IP-адреса')
        return v


class ServerCreate(ServerBase):
    """Cхема для добавления сервера."""

    ip_address: str = Field(description='IP-адрес сервера')
    domain_name: str = Field(description='Доменное имя')
    protocol: VPNProtocol = Field(description='Протокол работы сервера')
    is_active: bool = Field(description='Доступность сервера')
    region_code: str = Field(description='Код региона')


class ServerUpdate(ServerBase):
    """Cхема для обновления серверов."""
    region_code: str | None = Field(default=None,
                                    description='Код региона')


class ServerDB(ServerBase):
    """Схема выдачи данных о сервере."""

    model_config = ConfigDict(from_attributes=True)


class ServerWithRegionDB(ServerDB):
    """Схема выдачи данных о сервере."""

    region: RegionDB
