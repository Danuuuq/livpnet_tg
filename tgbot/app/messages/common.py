from collections import defaultdict


class CommonMessage:
    """Общие сообщения: приветствия, FAQ и др."""

    HELLO_FOR_CLIENT = (
        '👋 С возвращением, {name}!\n\n'
        'Вот твои активные подписки:\n\n'
        '{subscriptions_info}'
        '\nМы напомним тебе за день до окончания каждой подписки.\n'
        'Наслаждайся свободой в интернете или выбери действия ниже:'
    )
    HELLO_WITHOUT_SUB = (
        '👋Привет, {name}!\n😔У тебя пока нет подписки\n'
        'Оформляй себе подписку и приглашай друзей\n'
        'ведь за друзей мы даем деньги:')
    REFERRAL_INFO_MESSAGE = (
        '🚀 <b>Твоя реферальная программа</b>\n\n'
        '📎 Отправляй ссылку друзьям и получи 100 рублей:\n'
        '<code>https://t.me/livpnet_bot?start={tg_id}</code>\n\n'
        '💸 <b>Баланс</b>\n'
        'Доступно к выводу: <b>{available_to_withdraw}₽</b> за <b>{available_user_count}</b> оплативших\n'
        'Уже выведено: <b>{already_withdrawn}₽</b> за <b>{withdrawn_user_count}</b> человек(а)\n\n'
        '😊 Бонус начисляется, когда приглашённый оплатит подписку.\n'
        '👇 Чтобы вывести средства — напиши в поддержку!'
    )
    SUBSCRIPTION_WELCOME = (
        'В данный момент у тебя нет активной подписки.🤷‍♂️\n'
        'А значит можешь получить её бесплатно!🍾\n'
        'Либо сразу оплатить подписку.❤️')
    SUBSCRIPTIONS_INFO = (
        "<b>📦 Твои активные подписки:</b>\n\n"
        "{subscriptions}"
        "\nℹ️ Мы напомним тебе за день до окончания каждой подписки."
    )
    BAD_CREATE_TRIAL_SUB = (
        'У тебя уже был пробный период или подписка 🙈\n'
        'Хочешь бесплатно? Приглашай друзей и получай деньги 🧑‍🤝‍🧑\n'
        'А пока можем предложить оплатить текущую 😏:')
    PRICE_MESSAGE = (
        '<b>💼 Тарифы на подписку:</b>\n\n'
        '<b>🔹 2 устройства:</b>\n'
        '• 1 месяц — <b>250 ₽</b>\n'
        '• 6 месяцев — <b>1 400 ₽</b>\n'
        '• 1 год — <b>2 700 ₽</b>\n\n'
        '<b>🔸 4 устройства:</b>\n'
        '• 1 месяц — <b>450 ₽</b>\n'
        '• 6 месяцев — <b>2 500 ₽</b>\n'
        '• 1 год — <b>4 800 ₽</b>\n\n'
        'Выберите удобный вариант и оформите подписку 👇')
    URL_FOR_PAY = (
        "<b>💳 Оплата подписки</b>\n\n"
        "<b>Тип подписки:</b> {type}\n"
        "<b>Длительность:</b> {duration}\n"
        "<b>Количество устройств:</b> {type}\n"
        "<b>Протокол:</b> {protocol}\n"
        "<b>Регион:</b> {region_code}\n"
        "<b>Стоимость:</b> {amount} ₽\n\n"
        "Оплатите подписку по кнопке ниже.\n\n"
        "После оплаты в разделе подписок будут доступны сертификаты."
    )
    URL_FOR_PAY_RENEW = (
        "<b>💳 Продление подписки</b>\n\n"
        "<b>Тип подписки:</b> {type}\n"
        "<b>Длительность:</b> {duration}\n"
        "<b>Количество устройств:</b> {type}\n"
        "<b>Регион:</b> {region_code}\n"
        "<b>Стоимость:</b> {amount} ₽\n\n"
        "Оплатите подписку по кнопке ниже.\n\n"
        "После оплаты в разделе подписок будут доступны сертификаты."
    )
    URL_WITH_HELP = {
        'openvpn': {
            'windows': 'https://telegra.ph/Instrukciya-po-podklyucheniyu-k-OpenVPN-na-Windows-s-ispolzovaniem-klyuchej-07-07',
            'macos': 'https://telegra.ph/Instrukciya-po-podklyucheniyu-k-OpenVPN-na-macOS-s-ispolzovaniem-klyuchej-07-07',
            'android': 'https://telegra.ph/Instrukciya-po-podklyucheniyu-k-OpenVPN-na-Android-s-ispolzovaniem-klyuchej-07-07',
            'iphone': 'https://telegra.ph/Instrukciya-po-podklyucheniyu-k-OpenVPN-na-iOS-s-ispolzovaniem-klyuchej-07-07'
        },
        'vless': {
            'windows': 'https://telegra.ph/Vless-na-Windows-05-17',
            'macos': 'https://telegra.ph/Vless-na-MacOS-05-17',
            'android': 'https://telegra.ph/Vless-na-Adnroid-05-17',
            'iphone': 'https://telegra.ph/Vless-na-Iphone-05-17'
        }
    }
    LOAD_MSG_SUB = 'Загружаю информацию о подписке'
    LOAD_MSG_TRIAL_SUB = 'Оформляем пробную подписку'
    LOAD_MSG_KEYS = 'Начинаю загрузку ключей'
    LOAD_MSG_REF = 'Загружаю информацию по реферам'
    LOAD_MSG_PRICE = 'Загружаю информацию по ценам'
    LOAD_MSG_FAQ = 'Загружаю информацию с инструкциями'
    LOAD_MSG_SUPPORT = 'Перевожу на техническую поддержку'
    LOAD_MSG_CHOICE_SUB = 'Начинаем оформление подписки'
    CHOICE_MSG_FAQ_DEVICE = 'Выберите устройство:'
    CHOICE_MSG_PROTOCOL = 'Выберите протокол подключения:'
    CHOICE_MSG_NEW_OR_OLD = 'Продлеваем, обновляем или покупаем новую подписку?'
    CHOICE_MSG_TYPE_SUB = 'Выбери вариант подписки:'
    CHOICE_MSG_LOCATION = 'Выбери локацию для подключения:'
    CHOICE_MSG_DURATION = 'Выбери на какой срок оформишь подписку:'
    MSG_FOR_UPDATE_SUB = 'Выбери подписку, которую хочешь изменить:'
    MSG_FOR_RENEW_SUB = 'Выбери подписку, которую хочешь продлить:'
    MSG_FOR_TROUBLE = 'Расскажи о своей проблеме, '
    MSG_WITHOUT_SUB = 'У тебя пока что нет активных подписок:'
    MSG_FOR_OVPN = 'Скачивай, настраивай и подключайся:'
    MSG_FOR_VLESS = ('Сканируй QR-код или копируй ссылку: '
                     '<code>{url}</code>')

    @staticmethod
    def format_price_message(tariffs: list[dict]) -> str:
        grouped = defaultdict(list)
        for item in tariffs:
            grouped[item["type"]].append((item["duration"], item["price"]))

        parts = ['<b>💼 Тарифы на подписку:</b>\n']
        for i, (device_type, options) in enumerate(grouped.items()):
            bullet = "🔹" if i % 2 == 0 else "🔸"
            parts.append(f'\n<b>{bullet} {device_type}:</b>')
            for duration, price in options:
                parts.append(f'• {duration} — <b>{price} ₽</b>')
        parts.append('\n\nВыберите удобный вариант и оформите подписку 👇')
        return '\n'.join(parts)

    @staticmethod
    def format_start_message(
        name: str,
        main_menu: bool,
        subscriptions: list[dict] | None = None,
    ) -> str:
        """Формирует полное приветственное сообщение с учётом подписок."""
        if not subscriptions:
            if main_menu:
                return CommonMessage.HELLO_WITHOUT_SUB.format(
                    name=name,
                    subscriptions_info=subscriptions,
                )
            return CommonMessage.SUBSCRIPTION_WELCOME.format(
                name=name,
                subscriptions_info=subscriptions,
            )
        lines = []
        for idx, sub in enumerate(subscriptions, start=1):
            if sub.get('is_active') is False:
                continue
            region = sub.get('region').get('name', '❓Регион неизвестен')
            end_date = sub.get('end_date', '')[:10]
            sub_type = sub.get('type', 'неизвестно')
            protocol = sub.get('protocol', '❓Протокол неизвестен')
            lines.append(
                f'🔹 <b>Подписка №{idx}</b>\n'
                f'Тип: {sub_type}\n'
                f'Регион: {region}\n'
                f'Протокол: {protocol}\n'
                f'До: <b>{end_date}</b>\n'
            )
        subs_info = ('\n'.join(lines) if lines else 
                     'У всех подписок закончился оплаченный период 😔\n')
        if main_menu:
            return CommonMessage.HELLO_FOR_CLIENT.format(
                    name=name,
                    subscriptions_info=subs_info,
                )
        return CommonMessage.SUBSCRIPTIONS_INFO.format(subscriptions=subs_info)


class NotifyMessage:
    """Тексты для оповещения клиентов."""

    TOMORROW_EXPIRE_TEMPLATE = (
        '⏲️ Ваша подписка ({type}, {region}, {protocol}) '
        'заканчивается завтра.\n'
        'Не забудь продлить её, чтобы избежать отключения.'
    )
    EXPIRED_TEMPLATE = (
        '😪 Ваша подписка ({type}, {region}, {protocol}) отключена, '
        'так как срок действия завершился.\n'
        'Ваши сертификаты отключены и необходимо продлить или оформить новую.'
    )


class Keyboards:
    """Текст и ссылки для клавиатуры"""

    SUBSCRIPTION = '🔐 Твои подписки'
    REFERRAL = '🎁 Реферальная ссылка'
    PRICE = '💰 Стоимость подписок'
    HELP = '🆘 Инструкции и поддержка'
    PAY = '💳 Покупка'
    KEY = '🔐 Ключи к VPN'
    TRIAL = '🆓 Пробная подписка'
    RETURN = '🔙 Вернуться в меню'
    RETURN_CALLBACK = 'main_menu'
    TWO_DEVICE = '2️⃣ 2 устройства'
    FOUR_DEVICE = '4️⃣ 4 устройства'
    ONE_MONTH = '1️⃣ 1 месяц'
    SIX_MONTH = '6️⃣ 6 месяцев'
    TWELVE_MONTH = '1️⃣2️⃣ 12 месяцев'
    VLESS = '➰ Vless'
    VLESS_CALLBACK = 'vless'
    OVPN = '🧱 OpenVPN'
    OVPN_CALLBACK = 'openvpn'
    EXTENSION = '⏭️ Продлеваем'
    UPDATE = '🔁 Обновляем'
    NEW = '🆕 Новая'
    WINDOWS = '🪟 Windows'
    MAX = '🍏 Mac'
    ANDROID = '🤖 Android'
    IPHONE = '🍏 Iphone'
    SUPPORT = '🆘 Техническая поддержка'
    URL_SUPPORT = 'https://t.me/livpnet_support'
