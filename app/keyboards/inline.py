from typing import Any

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.messages.common import CommonMessage


def main_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в главном меню."""
    inline_kb_list = [
        [InlineKeyboardButton(text='🔐 Твоя подписка', callback_data='get_subscription')],
        [
            InlineKeyboardButton(text='🎁 Реферальная ссылка', callback_data='get_ref_url'),
            InlineKeyboardButton(text='💰 Стоимость подписок', callback_data='get_price')
        ],
        [InlineKeyboardButton(text='🆘 Инструкции и поддержка', callback_data='get_help')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def subscription_inline_kb(trial: bool = False) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в подписках."""
    inline_kb_list = [
        [InlineKeyboardButton(text='💳 Покупка', callback_data='pay_subscription')],
        [InlineKeyboardButton(text='🔐 Ключи к VPN', callback_data='get_certificate'),
         InlineKeyboardButton(text='🆘 Инструкции и поддержка', callback_data='get_help')],
    ]
    if trial:
        inline_kb_list.append(
            [InlineKeyboardButton(text='🆓 Пробная подписка', callback_data='get_trial')])
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_type_inline_kb(trial: bool = False) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text='2️⃣ 2 устройства', callback_data='2_device')],
        [InlineKeyboardButton(text='4️⃣ 4 устройства', callback_data='4_device')],
    ]
    if trial:
        inline_kb_list.append(
            [InlineKeyboardButton(text='🆓 Пробная подписка', callback_data='get_trial')])
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_duration_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text='1️⃣ 1 месяц', callback_data='1_month')],
        [InlineKeyboardButton(text='6️⃣ 6 месяцев', callback_data='2_month')],
        [InlineKeyboardButton(text='1️⃣2️⃣ 12 месяцев', callback_data='12_month')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_location_kb(servers: Any | dict,
                       ) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором региона сервера."""
    region_codes = {
        s.get('region').get('code'): s.get('region').get('name')
        for s in servers}
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text=f'{name}', callback_data=f'{code}')
        ] for code, name in region_codes.items()
    ]
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню',
                              callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_protocol_kb(servers: Any | dict,
                       ) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором региона сервера."""
    protocols = {s.get('protocol') for s in servers}
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text=f'{protocol}', callback_data=f'{protocol}')
        ] for protocol in protocols
    ]
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def keys_inline_kb(active: bool = False) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в ключах и информационных блоках."""
    if active:
        inline_kb_list = [
            [InlineKeyboardButton(text='🆘 Инструкции и поддержка', callback_data='get_help')],
            [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')]
        ]
    else:
        inline_kb_list = [
            [InlineKeyboardButton(text='💳 Покупка', callback_data='pay_subscription')],
            [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def protocol_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в ключах."""
    inline_kb_list = [
        [InlineKeyboardButton(text='➰ Vless', callback_data='vless'),
         InlineKeyboardButton(text='🧱 OpenVPN', callback_data='openvpn')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_sub_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в выборе подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text='⏭️ Продлеваем', callback_data='extension_sub')],
        [InlineKeyboardButton(text='🔁 Обновляем', callback_data='update_sub')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def device_inline_kb(protocol: str) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в ключах."""
    inline_kb_list = [
        [InlineKeyboardButton(text='🪟 Windows',
                              url=CommonMessage.URL_WITH_HELP[protocol]['windows']),
         InlineKeyboardButton(text='🍏 Mac',
                              url=CommonMessage.URL_WITH_HELP[protocol]['macos'])],
        [InlineKeyboardButton(text='🤖 Android',
                              url=CommonMessage.URL_WITH_HELP[protocol]['android']),
         InlineKeyboardButton(text='🍏 Iphone',
                              url=CommonMessage.URL_WITH_HELP[protocol]['iphone'])],
        [InlineKeyboardButton(text='🆘 Техническая поддержка',
                              url='https://t.me/livpnet_support')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню',
                              callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
