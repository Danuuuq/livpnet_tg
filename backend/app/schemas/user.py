from pydantic import BaseModel, ConfigDict, Field

from app.schemas.subscription import SubscriptionInfoDB


class UserBase(BaseModel):
    """Базовая схема данных пользователя."""

    telegram_id: int = Field(description='telegram_id пользователя')
    refer_from_id: int | None = Field(default=None,
                                      description='id того, кто пригласил')


class UserCreate(UserBase):
    """Cхема для создания пользователя."""


class UserDB(UserBase):
    """Схема выдачи данных о пользователе."""
    subscription: list[SubscriptionInfoDB] | None = Field(
        default=None,
        description='Подписка пользователя (если есть)',
    )

    model_config = ConfigDict(from_attributes=True)
