from fastapi import Depends
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.services.subscription import subscription_service


router = RabbitRouter(url=settings.get_rabbit_url)


@router.delete(
    '',
    summary='Деактивация подписок и уведомление клиентов',
    response_description=(
        'Деактивация неоплаченных подписок и уведомление клиентов'
        ' об окончании скорейшем.'),
)
async def delete_subscriptions(
    session: AsyncSession = Depends(get_async_session),
):
    """Деактивация подписок и уведомление об окончании."""
    return await subscription_service.notify_about_subs(session, router)
