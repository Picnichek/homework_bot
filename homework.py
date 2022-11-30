import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import HTTPRequestError, ParseStatusError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN_YANDEX')
TELEGRAM_TOKEN = os.getenv('TOKEN_TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
# RETRY_PERIOD = 2
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверяет наличие всех токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        logging.error(error)
    else:
        logging.debug(f'Сообщение не отправлено ботом {message}')


def get_api_answer(timestamp):
    """Создает и отправляет запрос к эндпоинту."""
    try:
        params = {'from_date': timestamp}
        logging.info(f'отправка запроса на {ENDPOINT} с параметрами {params}')
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException:
        logging.error('ошибка "RequestException"')
    if response.status_code != HTTPStatus.OK:
        raise HTTPRequestError(response)
    return response.json()


def check_response(response):
    """Проверка полученного ответа от эндпоинта."""
    if not response:
        message = 'пустой запрос'
        raise KeyError(message)

    if not isinstance(response, dict):
        message = 'тип данных не является "dict"'
        logging.error(message)
        raise TypeError(message)

    if 'homeworks' not in response:
        message = 'нет ожидаемого ключа "homeworks"'
        logging.error(message)
        raise KeyError(message)

    if not isinstance(response.get('homeworks'), list):
        message = 'формат ответа не является list'
        logging.error(message)
        raise TypeError(message)
    return response['homeworks']


def parse_status(homework):
    """Извлекает из статус работы."""
    if not homework.get('homework_name'):
        logging.warning('Нет имени домашней работы')
    else:
        homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'status' not in homework:
        message = 'Нет ключа "status"'
        logging.error(message)
        raise ParseStatusError(message)

    verdict = HOMEWORK_VERDICTS.get(homework_status)

    if homework_status not in HOMEWORK_VERDICTS:
        message = f'неожиданный статус домашней работы {homework_status}'
        logging.error(message)
        raise KeyError(message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    last_send = {
        'error': None,
    }

    if not check_tokens():
        logging.critical(
            'Отсутствует обязательная переменная окружения.'
            'Программа принудительно остановлена.'
        )
        sys.exit(
            'Отсутствует обязательная переменная окружения.'
            'Программа принудительно остановлена.'
        )

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('Ответ пуст, нет домашних работ.')
            for homework in homeworks:
                message = parse_status(homework)
                if last_send.get(homework['homework_name']) != message:
                    send_message(bot, message)
                    last_send[homework['homework_name']] = message
            timestamp = response.get('current_date')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if last_send['error'] != message:
                send_message(bot, message)
                last_send['error'] = message
        else:
            last_send['error'] = None
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.DEBUG,
        stream=sys.stdout,
    )

    main()
