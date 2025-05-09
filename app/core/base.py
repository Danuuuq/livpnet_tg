"""Импорты класса Base и всех моделей для Alembic."""
from app.core.database import Base # noqa
from app.models.server import Certificate, Region, Server # noqa
from app.models.subscription import Subscription # noqa
from app.models.user import User # noqa