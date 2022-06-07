from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import emoji
from logger.logger import logger_wraps


@logger_wraps()
def menu_button() -> ReplyKeyboardMarkup:
    """Create menu button and return it

    :rtype: ReplyKeyboardMarkup"""

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False,
                                   resize_keyboard=True)
    keyboard.add(KeyboardButton(
        emoji.emojize('Меню   :desert_island:'))
    )
    return keyboard
