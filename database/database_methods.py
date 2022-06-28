from logger.logger import logger_wraps
from classes.database import db, User, HotelSearch
from peewee import DoesNotExist
from telebot.types import Message
from classes.data_class import UserData
from loader import my_bot


@logger_wraps()
def create_database() -> None:
    """Resets database tables and creates them

    :return: None"""

    with db:
        db.drop_tables([User, HotelSearch])
        db.create_tables([User, HotelSearch])


@logger_wraps()
def add_user_to_database(message: Message) -> None:
    """Adds a user to the database (if he is not in it). If a user
     with such a chat_id is already in the database, then nothing happens

    :param message: argument
    :type message: Message object
    :return: None"""

    with db:
        try:
            User.get(User.chat_id == message.chat.id)
        except DoesNotExist:
            User.create(chat_id=message.chat.id)


@logger_wraps()
def add_results_to_database(message: Message, result: str) -> None:
    """Adds the result of the entered command to the database

    :param: result: the result of the entered command (one of the found hotels)
    :type: result: string
    :return: None
    """

    current_user = UserData.get_user(message.chat.id)
    with db:
        user = User.get(User.chat_id == message.chat.id)
        HotelSearch.create(users_information=user.id,
                           command=current_user.current_command,
                           result_of_command=result + f'\nСайт отеля https://hotels.com/ho{current_user.hotel_id}')


@logger_wraps()
def pull_from_database(message: Message) -> None:
    """Retrieves the results of the entered commands from the database.
    If there is an attempt to call the history command at the very beginning
    of the script call, an exception is processed and a message
    about the absence of data in the database is displayed.

    :param message: argument
    :type message: Message object
    :return: None"""

    try:
        HotelSearch.get()
        all_results = HotelSearch.select(
            HotelSearch, User).join(User).where(User.chat_id == message.chat.id)
        for i_element in all_results:
            my_bot.send_message(chat_id=message.chat.id,
                                text=f'*Команда: {i_element.command}\n*'
                                     f'*Дата и время введения введения: {i_element.date_of_command}\n\n*'
                                     f'{i_element.result_of_command}\n', disable_web_page_preview=True,
                                parse_mode='Markdown')

    except DoesNotExist:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*В настоящее время здесь ничего нет)*',
                            parse_mode='Markdown')
