import functools

import telebot.types
from loguru import logger
from copy import deepcopy
from telebot.types import Message
from classes.data_class import UserData

logger.add('./logger/log_file.log', rotation='100 MB', retention='1 day')


# TODO Интересно ваше мнение на счет реализации декоратора
def logger_wraps(*, entry=True, exit=True, level="INFO"):
    """Decorates functions by adding information about their call
    and exit from it (when you finish working with it)"""

    def wrapper(function):
        name = function.__name__

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)

            if entry:
                if len(args) > 0 and isinstance(args[0], Message):
                    logger_.log(level, "{} is entering '{}' (args={}, kwargs={})",
                                UserData.get_user(args[0].chat.id).user_name,
                                name, args, kwargs)
                elif len(kwargs) > 0 and isinstance(kwargs['message'], Message):
                    logger_.log(level, "{} is entering '{}' (args={}, kwargs={})",
                                UserData.get_user(kwargs['message'].chat.id).user_name,
                                name, args, kwargs)
                else:
                    logger_.log(level, "Entering '{}' (args={}, kwargs={})",
                                name, args, kwargs)
            result = function(*args, **kwargs)
            if exit:
                result_ = deepcopy(result)
                if type(result) is tuple and len(result) > 1 and (
                        'x-rapidapi-key' in result[0]):
                    result_[0]['x-rapidapi-key'] = 'XXX'
                if name == 'create_text_message':
                    result_ = 'there should be a message text'

                if len(args) > 0 and isinstance(args[0], Message):
                    logger_.log(level, "{} is exiting '{}' (result={})",
                                UserData.get_user(args[0].chat.id).user_name,
                                name, result_)
                elif len(kwargs) > 0 and isinstance(kwargs['message'], Message):
                    logger_.log(level, "{} is exiting '{}' (result={})",
                                UserData.get_user(kwargs['message'].chat.id).user_name,
                                name, result_)
                else:
                    logger_.log(level, "Exiting '{}' (result={})", name, result_)
            return result

        return wrapped

    return wrapper


