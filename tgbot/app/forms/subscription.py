from aiogram.fsm.state import State, StatesGroup


class SubscriptionForm(StatesGroup):
    """Класс формы для оформления подписки."""

    servers = State()
    type = State()
    location = State()
    protocol = State()
    count_device = State()
    duration = State()
    extension = State()


class SupportForm(StatesGroup):
    """Класс формы для пробной подписки."""

    device = State()
    protocol = State()
