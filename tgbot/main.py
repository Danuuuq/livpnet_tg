import asyncio

from aiohttp import web
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application
)

from app.core.bot import bot, set_commands
from app.core.config import settings
from app.core.dispatcher import dp
from app.core.logger import logger # noqa


async def on_startup() -> None:
    """Действия при запуске бота."""
    await set_commands()
    await bot.set_webhook(settings.get_webhook_url)
    await bot.send_message(chat_id=settings.ADMINS, text='Бот запущен')


async def on_shutdown() -> None:
    """Действия при остановке бота."""
    await bot.send_message(chat_id=settings.ADMINS, text='Бот остановлен!')
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


def main():
    """Запуск приложения с ботом."""

    if settings.WEBHOOK_MODE:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        web.run_app(app, host=settings.APP_HOST, port=settings.APP_PORT)
    # else:
    #     try:
    #         await bot.delete_webhook(drop_pending_updates=True)
    #         await dp.start_polling(
    #             bot, allowed_updates=dp.resolve_used_update_types())
    #     finally:
    #         await bot.session.close()


if __name__ == '__main__':
    # asyncio.run(main())
    main()
