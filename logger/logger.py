import functools
from loguru import logger
from copy import deepcopy
from telebot.types import Message

logger.add('./logger/log_file.log', rotation='100 MB', retention='1 day')


# def logger_wraps(*, entry=True, exit=True, level="INFO"):
#     """Decorates functions by adding information about their call
#     and exit from it (when you finish working with it)"""
#
#     def wrapper(function):
#         name = function.__name__
#
#         @functools.wraps(function)
#         def wrapped(*args, **kwargs):
#             logger_ = logger.opt(depth=1)
#
#             if entry:
#                 logger_.log(level, "Entering '{}' (args={}, kwargs={})",
#                             name, args, kwargs)
#             result = function(*args, **kwargs)
#             if exit:
#                 result_ = deepcopy(result)
#                 if type(result) is tuple and len(result) > 1 and 'x-rapidapi-key' in result[0]:
#                     result_[0]['x-rapidapi-key'] = 'XXX'
#                 if name == 'create_text_message':
#                     result_ = 'there should be a message text here'
#                 logger_.log(level, "Exiting '{}' (result={})", name, result_)
#             return result
#
#         return wrapped
#
#     return wrapper


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
                                args[0].from_user.first_name, name, args, kwargs)
                else:
                    logger_.log(level, "Entering '{}' (args={}, kwargs={})",
                                name, args, kwargs)
            result = function(*args, **kwargs)
            if exit:
                result_ = deepcopy(result)
                if type(result) is tuple and len(result) > 1 and 'x-rapidapi-key' in result[0]:
                    result_[0]['x-rapidapi-key'] = 'XXX'
                if name == 'create_text_message':
                    result_ = 'there should be a message text'
                if len(args) > 0 and isinstance(args[0], Message):
                    logger_.log(level, "{} is exiting '{}' (result={})", args[0].from_user.first_name, name, result_)
                else:
                    logger_.log(level, "Exiting '{}' (result={})", name, result_)
            return result

        return wrapped

    return wrapper