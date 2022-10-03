import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
from telegram import Bot

from exceptions import (ApiAnswerError,
                        BotMessageError,
                        EnvVariablesError,
                        ParseStatusError,
                        ResponseError)


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляет сообщение в чат телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as e:
        raise BotMessageError(
            f'Отправка сообщения невозможна: {e}')
    else:
        logger.info('Сообщение успешно отправлено!')


def get_api_answer(current_timestamp) -> dict:
    """Делает запрос к API и возвращает статусы работ."""
    if current_timestamp == 0:
        timestamp = 0
    else:
        timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise ApiAnswerError(
                f'Некорректный статус код: {response.status_code}'
            )
        return response.json()
    except Exception as e:
        raise ApiAnswerError(f'Возникла ошибка: {e}')


def check_response(response: dict) -> list:
    """Проверяет ответ API на корректность."""
    if isinstance(response, list):
        response = response[0]
    if not isinstance(response, dict):
        raise ResponseError('Некорректный ответ от API!')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise ResponseError('Домашки пришли не ввиде списка!')
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работы статус работы."""
    if not isinstance(homework, dict):
        raise ParseStatusError('Переменная "homework" не словарь!')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise KeyError('Отсутствует ключ "homework_name"!')
    if homework_status is None:
        logger.debug('Статус домашних работ не изменился.')

    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise ParseStatusError(
        f'Неизвестный статус домашней работы {homework_status}.')


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    for token in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        if token is None:
            logger.critical(
                'Отсутствует обязательная переменная окружения: '
                f'"{token}"!')
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit(0)

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)

            if response is None:
                logger.error('Не удалось получить ответ от API!')
                send_message(
                    bot,
                    'Проблема в "get_api_answer". Не удалось получить ответ!'
                )

            homework = check_response(response)
            count_homework = len(homework)
            if count_homework > 1:
                homework_status = parse_status(homework[0])
            else:
                homework_status = parse_status(homework)
            if homework_status:
                send_message(bot, homework_status)

            current_timestamp = int(time.time())
        except BotMessageError as ex:
            logger.error(ex)
        except (ApiAnswerError,
                EnvVariablesError,
                ParseStatusError,
                ResponseError) as ex:
            logger.error(ex)
            send_message(bot, ex)
        else:
            bot.start_polling()
            bot.idle()
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
