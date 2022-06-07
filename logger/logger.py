import functools
from loguru import logger
logger.add('./logger/log_file.log', rotation='100 MB', retention='1 day')



def logger_wraps(*, entry=True, exit=True, level="INFO"):
    """Decorates functions by adding information about their call
    and exit from it (when you finish working with it)"""

    def wrapper(function):
        name = function.__name__

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' ", name)
            result = function(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}", name)
            return result

        return wrapped

    return wrapper



