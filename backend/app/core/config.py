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

try:
    settings = Settings()
except ValidationError as error:
    missing_vars = [err["loc"][0] for err in error.errors()]
    raise EnvironmentError(
        f'Отсутствуют переменные окружения: {", ".join(missing_vars)}')
