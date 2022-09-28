import logging
import os
import requests
import time

from dotenv import load_dotenv
from telegram import Bot

from exceptions import IncorrectEnvVariables
from requests.exceptions import InvalidURL

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO)
logging.StreamHandler()


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API и возвращает статусы работ."""
    if type(current_timestamp) == int:
        timestamp = current_timestamp
    else:
        timestamp = int(time.time())
    params = {'from_date': timestamp}
    try:
        homeworks_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except InvalidURL:
        logging.error("Некорректный адрес, проверьте значение постоянной 'ENDPOINT'")
    except Exception as e:
        logging.error(f"Возникла непредвиденная ошибка: {e}")
    else:
        return homeworks_statuses.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    homeworks = response.get('homeworks')
    if type(homeworks) is list:
        return homeworks
    logging.error(f"Некорректный ответ от API! Значение ключа 'homeworks' отличается от ожидаемого {type(homeworks)} != list")
    

def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.critical("Отсутствует обязательная переменная окружения: 'PRACTICUM_TOKEN'!")
    if TELEGRAM_TOKEN is None:
        logging.critical("Отсутствует обязательная переменная окружения: 'TELEGRAM_TOKEN!'")
    if TELEGRAM_CHAT_ID is None:
        logging.critical("Отсутствует обязательная переменная окружения: 'TELEGRAM_CHAT_ID!'")
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        raise IncorrectEnvVariables('Некоторые переменные окружения не доступны!')

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    # main()
    print(check_response({'homeworks': (12312312312, 123,), 'current_date': 15}))
