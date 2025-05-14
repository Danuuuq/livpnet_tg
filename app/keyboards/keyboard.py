from typing import Sequence

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.models.server import Server


def chose_location_server_kb(servers: Sequence[Server]) -> ReplyKeyboardMarkup:
    """Инлайн клавиатура с выбором региона сервера."""
    kb_list = [
        [KeyboardButton(text=f'{server.region.name}')] for server in servers
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder="Выбери регион:")
    return keyboard