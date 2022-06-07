from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from logger.logger import logger_wraps


@logger_wraps()
def set_default_commands(my_bot):
    my_bot.set_my_commands(
        [BotCommand(*command) for command in DEFAULT_COMMANDS]
    )
