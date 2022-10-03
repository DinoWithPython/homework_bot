class EnvVariablesError(Exception):
    """Некорретные переменные окружения."""

    pass


class ParseStatusError(Exception):
    """Ошибка в функции `parse_status`."""

    pass


class ResponseError(Exception):
    """Ошибка в переменной `response`."""

    pass


class ApiAnswerError(Exception):
    """Некорректный ответ от API."""

    pass


class BotMessageError(Exception):
    """Отправка сообщения ботов невозможна."""

    pass
