import os

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Класс для базовых настроек приложения."""

    NAME_SCHEDULER: str = 'celery_worker'
    TIMEZONE: str = 'UTC'
    SERIALIZER_FORMAT: str = 'json'
    NOTIFY_PATH: str = 'notify'
    SUBSCRIPTION_PATH: str = 'subs'
    MAX_RETRIES: int = 3
    DEF_RETRY_DELAY: int = 5
    TG_HOST: str
    TG_PORT: int
    BACKEND_HOST: str
    BACKEND_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT_WEB: int
    RABBIT_PORT_AMQP: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '../../infra', '.env'),
        env_file_encoding='utf-8',
        extra='ignore')

    @property
    def get_backend_url(self) -> str:
        """Ссылка для подключения к redis."""
        return (f'http://{self.BACKEND_HOST}:{self.BACKEND_PORT}')

    @property
    def get_tgbot_url(self) -> str:
        """Ссылка для подключения к telegram."""
        return (f'http://{self.TG_HOST}:{self.TG_PORT}')

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
