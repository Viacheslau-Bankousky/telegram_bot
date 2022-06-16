from loader import my_bot
from utils.set_bot_commands import set_default_commands
from requests.exceptions import ConnectionError, ReadTimeout
from logger.logger import logger
from database.database_methods import create_database
from peewee import InternalError
from telebot.apihelper import ApiTelegramException
from handlers.default_handlers import *


if __name__ == '__main__':
    try:
        set_default_commands(my_bot)
        create_database()
        my_bot.infinity_polling(timeout=0)
    except (ConnectionError, ReadTimeout, InternalError,
            ApiTelegramException):
        logger.exception('ups... something went wrong')

