import os

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс для базовых настроек приложения."""

    APP_TITLE: str = 'Backend для ТГ-бота'
    APP_DESCRIPTION: str = (
        'Реализация бизнес-логики, взаимодействия с серверами, '
        'сервисами по оплате услуг и сбору информации.')
    API_KEY: str
    BACKEND_HOST: str
    BACKEND_PORT: int
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SHOP_ID: str
    SECRET_KEY_SHOP: str
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT_WEB: int
    RABBIT_PORT_AMQP: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '../../../infra', '.env'),
        env_file_encoding='utf-8',
        extra='ignore')

    @property
    def get_headers_auth(self) -> dict[str, str]:
        """Ссылка для подключения к базе данных."""
        return {'Authorization': f'Bearer {self.API_KEY}'}

    @property
    def get_db_url(self) -> str:
        """Ссылка для подключения к базе данных."""
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:'
                f'{self.POSTGRES_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}')

    @property
    def get_redis_url(self) -> str:
        """Ссылка для подключения к redis."""
        return (f'redis://{self.REDIS_USER}:'
                f'{self.REDIS_USER_PASSWORD}@'
                f'{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}')

    @property
    def get_redis_url_ssl(self) -> str:
        """Ссылка для подключения к redis SSL."""
        return (f'rediss://{self.REDIS_PASSWORD}@'
                f'{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}')

    @property
    def get_rabbit_url(self) -> str:
        """Ссылка для подключения к rabbitMQ."""
        return (f'amqp://{self.RABBITMQ_DEFAULT_USER}:'
                f'{self.RABBITMQ_DEFAULT_PASS}@'
                f'{self.RABBIT_HOST}:{self.RABBIT_PORT_AMQP}')


try:
    settings = Settings()
except ValidationError as error:
    missing_vars = [err["loc"][0] for err in error.errors()]
    raise EnvironmentError(
        f'Отсутствуют переменные окружения: {", ".join(missing_vars)}')
