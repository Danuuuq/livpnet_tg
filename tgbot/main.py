import asyncio

from app.core.bot import bot
from app.core.dispatcher import dp


async def main():
    """Запуск приложения с ботом."""

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
