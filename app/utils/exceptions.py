class SubscriptionNotFoundError(Exception):
    """Вызывается, если у пользователя не найдена подписка."""
    def __init__(self, user_id: int, message: str = "Подписка не найдена"):
        self.user_id = user_id
        self.message = message
        super().__init__(f"{message} (user_id={user_id})")
