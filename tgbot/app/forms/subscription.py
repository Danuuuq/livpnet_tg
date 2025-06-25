from aiogram.fsm.state import State, StatesGroup


class SubscriptionForm(StatesGroup):
    """Класс формы для оформления подписки."""

    servers = State()
    type = State()
    location = State()
    protocol = State()
    count_device = State()
    duration = State()
    subscription = State()


class SubscriptionExtensionForm(StatesGroup):
    """Класс формы для продления подписки."""

    extension = State()
    sub_id = State()
    type = State()


class SupportForm(StatesGroup):
    """Класс формы для пробной подписки."""

    device = State()
    protocol = State()
