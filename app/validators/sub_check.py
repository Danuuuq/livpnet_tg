from app.models import Subscription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime


async def is_subscription_active(user_id: int, db: AsyncSession) -> bool:
    subscription = await db.scalar(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.is_active is True,
            Subscription.end_date > datetime.now()
        )
    )
    return bool(subscription), subscription
