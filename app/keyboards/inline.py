from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def main_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в главном меню."""
    inline_kb_list = [
        [InlineKeyboardButton(text='🔐 Твоя подписка', callback_data='get_subscription')],
        [InlineKeyboardButton(text='🎁 Реферальная ссылка', callback_data='get_ref_url'),
         InlineKeyboardButton(text='💰 Стоимость подписок', callback_data='get_price')],
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
            [InlineKeyboardButton(text='🆓 Пробная подписка', callback_data='pay_subscription')])
    inline_kb_list.append(
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='/start')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
