from collections import defaultdict

class CommonMessage:
    """Общие сообщения: приветствия, FAQ и др."""

    HELLO_FOR_CLIENT = (
        '👋С возвращением, {name}!\nТвоя подписка активна до: {end_data:.10}\n'
        'Мы напомним тебе за день до окончания подписки, а пока '
        'наслаждайся свободой в интернете, или выбери действия:')
    HELLO_WITHOUT_SUB = (
        '👋Привет, {name}!\n😔У тебя пока нет подписки\n'
        'Оформляй себе подписку и приглашай друзей\n'
        'ведь за друзей мы даем бонусы (деньги):')
    REFERRAL_MESSAGE = (
        '🚀 Вот твоя персональная ссылка на приглашение: '
        '[нажми на ссылку для копирования] '
        '<code>https://t.me/livpnet_bot?start={user_id}</code>\n'
        'Скоро тут будет информация о твоем балансе\n'
        'Отправляй ссылку друзьям и получи 100 рублей 💵\n'
        'Бонус получишь, когда друг оплатят подписку.😊\n'
        'Вывод средств необходимо запросить через поддержку 👇')
    SUBSCRIPTION_WELCOME = (
        'В данный момент у тебя нет активной подписки.🤷‍♂️\n'
        'А значит можешь получить её бесплатно!🍾\n'
        'Либо сразу оплатить подписку.❤️')
    SUBSCRIPTION_INFO = (
        'Твоя подписка активна до: {end_date:.10}\n'
        'Твой текущий план подписки: {type}\n')
    BAD_CREATE_TRIAL_SUB = (
        'У тебя уже был пробный период или подписка 🙈\n'
        'Хочешь бесплатно? Приглашай друзей и получай бонусы 🧑‍🤝‍🧑\n'
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
        '<b>💳 Оплата подписки</b>\n\n'
        'Оплатите подписку по ссылке ниже:\n\n'
        '<a href=\'{payment_link}\'>👉 Перейти к оплате</a>\n\n'
        'После успешной оплаты проверяй свои подписки.'
    )
    URL_WITH_HELP = {
        'openvpn': {
            'windows': 'https://telegra.ph/OpenVPN-na-Windows-05-17',
            'macos': 'https://telegra.ph/OpenVPN-na-MacOS-05-17',
            'android': 'https://telegra.ph/OpenVPN-na-Android-05-17',
            'iphone': 'https://telegra.ph/OpenVPN-na-Iphone-05-17'
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
    CHOICE_MSG_NEW_OR_OLD = 'Продлеваем или меняем подписку?'
    CHOICE_MSG_TYPE_SUB = 'Выбери вариант подписки:'
    CHOICE_MSG_LOCATION = 'Выбери локацию для подключения:'
    CHOICE_MSG_DURATION = 'Выбери на какой срок оформишь подписку:'
    MSG_FOR_UPDATE_SUB = (
        'Обратите внимание, после обновления подписки\n'
        'старая останется действительной до конца срока действия\n'
        'Выбери вариант подписки:')
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


class Keyboards:
    """Текст для клавиатуры"""

    SUBSCRIPTION = '🔐 Твоя подписка'
    REFERRAL = '🎁 Реферальная ссылка'
    PRICE = '💰 Стоимость подписок'
    HELP = '🆘 Инструкции и поддержка'
    PAY = '💳 Покупка'
    KEY = '🔐 Ключи к VPN'
    TRIAL = '🆓 Пробная подписка'
    RETURN = '🔙 Вернуться в меню'
    TWO_DEVICE = '2️⃣ 2 устройства'
    FOUR_DEVICE = '4️⃣ 4 устройства'
    ONE_MONTH = '1️⃣ 1 месяц'
    SIX_MONTH = '6️⃣ 6 месяцев'
    TWELVE_MONTH = '1️⃣2️⃣ 12 месяцев'
    VLESS = '➰ Vless'
    OVPN = '🧱 OpenVPN'
    EXTENSION = '⏭️ Продлеваем'
    UPDATE = '🔁 Обновляем'
    WINDOWS = '🪟 Windows'
    MAX = '🍏 Mac'
    ANDROID = '🤖 Android'
    IPHONE = '🍏 Iphone'
    SUPPORT = '🆘 Техническая поддержка'
