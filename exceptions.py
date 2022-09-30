class IncorrectEnvVariables(Exception):
    """Некорретные переменные окружения."""

    pass


class IncorrectParseStatus(Exception):
    """Ошибка в функции `parse_status`."""

    pass


class IncorrectResponse(Exception):
    """Ошибка в переменной `response`."""

    pass


class IncorrectApiAnswer(Exception):
    """Некорректный ответ от API."""

    pass


class BotCanNotSendMessage(Exception):
    """Отправка сообщения ботов невозможна."""

    pass
