from loader import my_bot
from utils.set_bot_commands import set_default_commands
from requests.exceptions import ConnectionError, ReadTimeout
from handlers.default_handlers import *

if __name__ == '__main__':
    try:
        set_default_commands(my_bot)
        my_bot.infinity_polling(timeout=0)
    except (ConnectionError, ReadTimeout):
        pass
