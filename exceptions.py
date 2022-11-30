class HTTPRequestError(Exception):
    """Ошибка, возвращающая код ответа от API."""

    def __init__(self, response):
        message = (
            f'{response.url} недоступен. '
            f'Код ответа API: {response.status_code}]'
        )
        super().__init__(message)


class ParseStatusError(Exception):
    """Ошибка, возвращающая парсинг ответа от API."""

    def __init__(self, text):
        message = f'Парсинг ответа API: {text}'
        super().__init__(message)
