from app.core.broker import broker
from app.core.bot import bot
from app.keyboards.inline import keys_inline_kb
from app.messages.common import NotifyMessage
from app.schemas.subscription import SubscriptionNotifyDB


@broker.subscriber('notify_deactivate_sub')
async def send_notify_deactivate_sub(data: SubscriptionNotifyDB):
    await bot.send_message(
        chat_id=data.telegram_id,
        text=NotifyMessage.EXPIRED_TEMPLATE.format(
            type=data.type,
            region=data.region,
            protocol=data.protocol,
        ),
        reply_markup=keys_inline_kb()
    )


@broker.subscriber('notify_end_sub')
async def send_notify_end_sub(data: SubscriptionNotifyDB):
    await bot.send_message(
        chat_id=data.telegram_id,
        text=NotifyMessage.TOMORROW_EXPIRE_TEMPLATE.format(
            type=data.type.value,
            region=data.region,
            protocol=data.protocol.value,
        ),
        reply_markup=keys_inline_kb()
    )
