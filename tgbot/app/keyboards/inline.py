from typing import Any

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.messages.common import CommonMessage, Keyboards
from app.schemas.subscription import SubscriptionDuration, SubscriptionType


def main_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в главном меню."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.SUBSCRIPTION,
                              callback_data='get_subscription')],
        [
            InlineKeyboardButton(text=Keyboards.REFERRAL,
                                 callback_data='get_ref_url'),
            InlineKeyboardButton(text=Keyboards.PRICE,
                                 callback_data='get_price')
        ],
        [InlineKeyboardButton(text=Keyboards.HELP,
                              callback_data='get_help')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def subscription_inline_kb(trial: bool = False) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в подписках."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.PAY,
                              callback_data='pay_subscription')],
        [InlineKeyboardButton(text=Keyboards.KEY,
                              callback_data='get_certificate'),
         InlineKeyboardButton(text=Keyboards.HELP,
                              callback_data='get_help')],
    ]
    if trial:
        inline_kb_list.append(
            [InlineKeyboardButton(text=Keyboards.TRIAL,
                                  callback_data='get_trial')])
    inline_kb_list.append(
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_subscription_inline_kb(subscriptions: dict) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором подписки."""
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text=(f'{sub.get('region').get('name')} '
                      f'{sub.get('protocol')} '
                      f'до {sub.get('end_date')[:10]} '
                      f'на {sub.get('type')} '),
                callback_data=f'{sub.get('id')}')
        ] for sub in subscriptions
    ]
    inline_kb_list.append(
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_type_inline_kb(trial: bool = False) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором типа подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.TWO_DEVICE,
                              callback_data=SubscriptionType.devices_2)],
        [InlineKeyboardButton(text=Keyboards.FOUR_DEVICE,
                              callback_data=SubscriptionType.devices_4)],
    ]
    if trial:
        inline_kb_list.append(
            [InlineKeyboardButton(text=Keyboards.TRIAL,
                                  callback_data='get_trial')])
    inline_kb_list.append(
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_duration_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбором длительности подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.ONE_MONTH,
                              callback_data=SubscriptionDuration.month_1)],
        [InlineKeyboardButton(text=Keyboards.SIX_MONTH,
                              callback_data=SubscriptionDuration.month_6)],
        [InlineKeyboardButton(text=Keyboards.TWELVE_MONTH,
                              callback_data=SubscriptionDuration.year_1)],
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)]
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
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_protocol_kb(
    servers: Any | dict,
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
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def payment_kb(url: str) -> InlineKeyboardMarkup:
    """Инлайн клавиатура для оплаты подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text='Оплата на Ю.Касса', url=url)],
    ]
    inline_kb_list.append(
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def keys_inline_kb(
    subscriptions: list[dict] | None = None,
) -> InlineKeyboardMarkup:
    """Инлайн клавиатура в ключах и информационных блоках."""
    inline_kb_list = []
    if subscriptions:
        for sub in subscriptions:
            if sub.get("certificates"):
                for idx, certificate in enumerate(sub["certificates"]):
                    inline_kb_list.append([
                        InlineKeyboardButton(
                            text=(f'Сертификат {sub.get('region').get('name')}'
                                  f' {sub.get('protocol')} №{idx + 1}'),
                            url=certificate
                        )
                    ])
        inline_kb_list += [
            [InlineKeyboardButton(text=Keyboards.HELP,
                                  callback_data='get_help')],
            [InlineKeyboardButton(text=Keyboards.RETURN,
                                  callback_data=Keyboards.RETURN_CALLBACK)]
        ]
    else:
        inline_kb_list = [
            [InlineKeyboardButton(text=Keyboards.PAY,
                                  callback_data='pay_subscription')],
            [InlineKeyboardButton(text=Keyboards.RETURN,
                                  callback_data=Keyboards.RETURN_CALLBACK)]
        ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def keys_referral_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в блоке с реферралами."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.PAY,
                              callback_data='pay_subscription')],
        [InlineKeyboardButton(text=Keyboards.SUPPORT,
                              url=Keyboards.URL_SUPPORT)],
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def protocol_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в инструкции с выбором протокола."""
    inline_kb_list = [
        [
            # InlineKeyboardButton(text=Keyboards.VLESS,
            #                      callback_data=Keyboards.VLESS_CALLBACK),
            InlineKeyboardButton(text=Keyboards.OVPN,
                                 callback_data=Keyboards.OVPN_CALLBACK)
        ],
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def choice_sub_inline_kb() -> InlineKeyboardMarkup:
    """Инлайн клавиатура в выборе подписки."""
    inline_kb_list = [
        [InlineKeyboardButton(text=Keyboards.EXTENSION,
                              callback_data='renew_sub')],
        [InlineKeyboardButton(text=Keyboards.UPDATE,
                              callback_data='update_sub')],
        [InlineKeyboardButton(text=Keyboards.NEW,
                              callback_data='new_sub')],
        [InlineKeyboardButton(text=Keyboards.RETURN,
                              callback_data=Keyboards.RETURN_CALLBACK)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def device_inline_kb(protocol: str) -> InlineKeyboardMarkup:
    """Инлайн клавиатура выбора устройств."""
    inline_kb_list = [
        [InlineKeyboardButton(
            text=Keyboards.WINDOWS,
            url=CommonMessage.URL_WITH_HELP[protocol]['windows']),
         InlineKeyboardButton(
             text=Keyboards.MAX,
             url=CommonMessage.URL_WITH_HELP[protocol]['macos'])],
        [InlineKeyboardButton(
            text=Keyboards.ANDROID,
            url=CommonMessage.URL_WITH_HELP[protocol]['android']),
         InlineKeyboardButton(
             text=Keyboards.IPHONE,
             url=CommonMessage.URL_WITH_HELP[protocol]['iphone'])],
        [InlineKeyboardButton(
            text=Keyboards.SUPPORT,
            url=Keyboards.URL_SUPPORT)],
        [InlineKeyboardButton(
            text=Keyboards.RETURN,
            callback_data=Keyboards.RETURN_CALLBACK)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
