from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.core.config import settings
from .logger import logger # noqa

bot = Bot(token=settings.TOKEN_TG, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))


async def set_commands():
    """Добавление команд для взаимодействия с ботом"""
    commands = [BotCommand(command='start', description='Перезапуск'),
                BotCommand(command='main', description='Главное меню')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
