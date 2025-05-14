from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Certificate
from app.crud.base import CRUDBase


class CRUDCertificate(CRUDBase[dict, Certificate]):
    """Круды для сертификатов.

    Методы:
    get_by_filename: получить из БД .ovpn по имени;
    create_certificate: создать сертификат.
    """
    async def get_by_filename(
        self,
        filename: str,
        session: AsyncSession
    ) -> Certificate | None:
        result = await session.execute(
            select(Certificate).where(Certificate.filename == filename)
        )
        return result.scalars().first()

    async def create_certificate(
        self,
        session: AsyncSession,
        *,
        filename: str,
        subscription_id: int,
        server_id: int | None = None
    ) -> Certificate:
        obj_in = {
            'filename': filename,
            'subscription_id': subscription_id,
            'server_id': server_id,
        }
        return await self.create(obj_in, session)


certificate_crud = CRUDCertificate(Certificate)
