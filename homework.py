import logging
import os
import requests
import time

from dotenv import load_dotenv
from telegram import Bot

from exceptions import (BotCanNotSendMessage,
                        IncorrectApiAnswer,
                        IncorrectEnvVariables,
                        IncorrectParseStatus,
                        IncorrectResponse)
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
    level=logging.DEBUG)
logging.StreamHandler()


def send_message(bot, message):
    """Отправляет сообщение в чат телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as e:
        logging.error(
            f'Возникла непредвиденная ошибка: {e}.'
            ' Отправка сообщения не возможна.')
        raise BotCanNotSendMessage(
            f'Возникла непредвиденная ошибка: {e}. '
            'Отправка сообщения не возможна.')
    else:
        logging.info('Сообщение успешно отправлено!')


def get_api_answer(current_timestamp) -> dict:
    """Делает запрос к API и возвращает статусы работ."""
    timestamp = current_timestamp or int(time.time())

    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            status_code = response.status_code
            logging.error(f'Некорректный статус код: {status_code}')
            raise IncorrectApiAnswer(f'Некорректный статус код: {status_code}')
        return response.json()
    except InvalidURL:
        logging.error('Проверьте значение постоянной "ENDPOINT"')
        raise InvalidURL('Проверьте значение постоянной "ENDPOINT"')
    except ValueError:
        logging.error('Не удалось преобразовать статус работы к словарю.')
        raise ValueError('Не удалось преобразовать статус работы к словарю.')
    except AssertionError:
        logging.error('Не удалось преобразовать статус работы к словарю.')
        raise ValueError('Не удалось преобразовать статус работы к словарю.')
    except Exception as e:
        logging.error(f'Возникла непредвиденная ошибка: {e}')
        raise IncorrectApiAnswer(f'Возникла непредвиденная ошибка: {e}')


def check_response(response: dict) -> list:
    """Проверяет ответ API на корректность."""
    if response is None:
        logging.error('Переменная "response" не содержит ничего!')
        raise IncorrectResponse('Некорректный ответ от API!')
    if type(response) is not dict:
        logging.error('Переменная "response" не словарь!')
        raise TypeError('Некорректный ответ от API!')
    if response == {}:
        logging.error('П"response" содержит пустой словарь!')
        raise IncorrectResponse('"response" содержит пустой словарь!')

    try:
        homeworks = response.get('homeworks')
        if type(homeworks) is not list:
            logging.error('Домашки пришли не ввиде списка!')
            raise IncorrectResponse('Домашки пришли не ввиде списка!')
        return homeworks
    except AttributeError:
        logging.error('Некорректный ответ от API!')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работы статус работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status is None:
        logging.debug('Статус домашних работ не изменился.')
        return False

    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'

    logging.error(f'Неизвестный статус домашней работы {homework_status}.')
    raise IncorrectParseStatus(
        f'Неизвестный статус домашней работы {homework_status}.')


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.critical(
            'Отсутствует обязательная переменная окружения: '
            '"PRACTICUM_TOKEN"!')
    if TELEGRAM_TOKEN is None:
        logging.critical(
            'Отсутствует обязательная переменная окружения: '
            '"TELEGRAM_TOKEN!"')
    if TELEGRAM_CHAT_ID is None:
        logging.critical(
            'Отсутствует обязательная переменная окружения: '
            '"TELEGRAM_CHAT_ID!"')
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise IncorrectEnvVariables('Переменные окружения не доступны!')

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)

            if get_api_answer(current_timestamp) is None:
                logging.error('Не удалось получить ответ от API!')
                send_message(
                    bot,
                    'Проблема в "get_api_answer". Не удалось получить ответ!'
                )

            homework = check_response(response)
            if homework is None:
                logging.error('Не корректный ответ API!')
                send_message(
                    bot,
                    'Проблема в функции "check_response". API некорректен.'
                )

            count_homework = len(homework)
            if count_homework > 1:
                homework_status = parse_status(homework[0])
            else:
                homework_status = parse_status(homework)
            if homework_status:
                send_message(bot, homework_status)

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except IncorrectApiAnswer as error:
            message = ('Возникла непредвиденная ошибка'
                       f' в функции "get_api_answer": {error}')
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            bot.start_polling()
            bot.idle()


if __name__ == '__main__':
    main()
