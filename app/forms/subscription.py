from aiogram.fsm.state import State, StatesGroup


class TrialSubForm(StatesGroup):
    """Класс формы для пробной подписки."""

    location = State()


class SubscriptionForm(TrialSubForm):
    count_device = State()
    duration = State()
