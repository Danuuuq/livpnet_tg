from enum import Enum


class BaseEnum(Enum):
    def format(self, **kwargs) -> str:  # noqa
        """Форматирование строки с подстановкой параметров."""
        return self.value.format(**kwargs)


class Errors(str, BaseEnum):
    BASE_ERROR = 'Произошла ошибка: {e}'


class Messages(str, BaseEnum):
    NOT_SUB = 'У вас нет активной подписки.'
    TEST = 'Тут будет сертификат, а пока тестируем ответ.'
