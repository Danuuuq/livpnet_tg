import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.variables import SettingFieldDB

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class VPNProtocol(str, enum.Enum):
    openvpn = "OpenVPN"
    vless = "Vless"


class Region(Base):
    """Модель для регионов."""

    code: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_CODE_REGION),
        unique=True, nullable=False)
    name: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_NAME),
        unique=True, nullable=False)

    servers: Mapped[list['Server']] = relationship(
        'Server', back_populates='region')

    subscriptions: Mapped[list['Subscription']] = relationship(
        'Subscription', back_populates='region')


class Server(Base):
    """Модель для серверов."""

    ip_address: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_IP), nullable=False, unique=True)
    domain_name: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_NAME), nullable=False, unique=True)
    protocol: Mapped[VPNProtocol] = mapped_column(
        Enum(VPNProtocol), nullable=False) 
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=SettingFieldDB.DEFAULT_ACTIVE_SRV, nullable=False)
    max_certificates: Mapped[int] = mapped_column(
        Integer, default=SettingFieldDB.DEFAULT_MAX_CERT, nullable=False)
    current_cert_count: Mapped[int] = mapped_column(
        Integer, default=SettingFieldDB.DEFAULT_FOR_COUNT, nullable=False)

    region_id: Mapped[int] = mapped_column(
        ForeignKey('region.id'), nullable=True)
    region: Mapped['Region'] = relationship(
        'Region', remote_side='Region.id', back_populates='servers')

    certificates: Mapped[list['Certificate']] = relationship(
        'Certificate', back_populates='server')


class Certificate(Base):
    """Модель для сертификатов."""

    filename: Mapped[str] = mapped_column(
        String(SettingFieldDB.MAX_LENGTH_FILENAME),
        nullable=False, unique=True)
    url_vless: Mapped[str] = mapped_column(
        Text, nullable=True, unique=True
    )

    server_id: Mapped[int] = mapped_column(
        ForeignKey('server.id'), nullable=True)
    server: Mapped['Server'] = relationship(
        'Server', remote_side='Server.id',
        back_populates='certificates')

    subscription_id: Mapped[int] = mapped_column(
        ForeignKey('subscription.id'), nullable=True)
    subscription: Mapped['Subscription'] = relationship(
        'Subscription', remote_side='Subscription.id',
        back_populates='certificates')
