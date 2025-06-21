import asyncio

from aiohttp import ClientSession

from app.core.bot import bot
from app.core.dispatcher import dp
from app.core.logger import logger # noqa


async def main():
    """Запуск приложения с ботом."""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        bot.http_client = ClientSession()
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await bot.http_client.close()


if __name__ == '__main__':
    asyncio.run(main())
