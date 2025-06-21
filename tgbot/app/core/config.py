import os

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс для базовых настроек приложения."""

    TOKEN_TG: str
    ADMINS: str
    DOMAIN_NAME: str
    TG_HOST: str
    TG_PORT: int
    WEBHOOK_SECRET: str
    WEBHOOK_PATH: str = '/webhook'
    BACKEND_HOST: str
    BACKEND_PORT: int
    AUTH_PATH: str = '/auth/'
    SERVER_PATH: str = '/server/active'
    SUBSCRIPTION_PATH: str = '/subscription/'
    PRICE_PATH: str = 'price'

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '../../../infra', '.env'),
        env_file_encoding='utf-8',
        extra='ignore')

    @property
    def get_webhook_url(self) -> str:
        """Ссылка для webhook подключений."""
        return f'https://{self.DOMAIN_NAME}{self.WEBHOOK_PATH}'

    @property
    def get_backend_url(self) -> str:
        """Ссылка для обращений к backend."""
        return f'http://{self.BACKEND_HOST}:{self.BACKEND_PORT}'


try:
    settings = Settings()
except ValidationError as error:
    missing_vars = [err["loc"][0] for err in error.errors()]
    raise EnvironmentError(
        f'Отсутствуют переменные окружения: {", ".join(missing_vars)}')
