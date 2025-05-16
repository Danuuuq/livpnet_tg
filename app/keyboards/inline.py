from typing import Sequence

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.models.server import Server


def main_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в главном меню."""
    inline_kb_list = [
        [InlineKeyboardButton(text='🔐 Твоя подписка', callback_data='get_subscription')],
        [
            InlineKeyboardButton(text='🎁 Реферальная ссылка', callback_data='get_ref_url'),
            InlineKeyboardButton(text='💰 Стоимость подписок', callback_data='get_price')
        ],
        [InlineKeyboardButton(text='🆘 Подсказки и советы', callback_data='get_information')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def subscription_inline_kb(status: str | None = None) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в подписках."""
    inline_kb_list = [
        [InlineKeyboardButton(text='💳 Приобретение', callback_data='pay_subscription')],
        [InlineKeyboardButton(text='🔐 Ключи к VPN', callback_data='get_certificate'),
         InlineKeyboardButton(text='🆘 Помощь', callback_data='get_help')],
    ]
    if status == 'trial':
        inline_kb_list.append(
            [InlineKeyboardButton(text='🆓 Пробная подписка', callback_data='get_trial')])
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='/start')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def chose_location_server_kb(servers: Sequence[Server]) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором региона сервера."""
    inline_kb_list = [
        [InlineKeyboardButton(text=f'{server.region.name}',
                              callback_data=f'{server.region.code}')] for server in servers
    ]
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='/start')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
