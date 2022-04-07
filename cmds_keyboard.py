from telebot import types
import emoji
from loader import my_bot
from classes import User
from classes import MyTranslationCalendar
import handlers


def commands_keyboard(message: types.Message) -> None:
    """Inline keyboard with options for the main most used
    commands (the /hello-world command is not displayed specifically,
    in view of its remoteness from the main logic of the bot; command
    /help is not displayed because the menu command is available throughout
    the execution of the entire script).The id of the message with the inline
    keyboard is recorded in a special field of the User class (also the flag field
    is activated), for its further deletion (if necessary). The displayed menu removes
    the previous inline keyboards. All dynamic attributes of the class
    object are updated

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text=emoji.emojize('LOWPRICE  :money-mouth_face:'),
            callback_data='/lowprice'),
        types.InlineKeyboardButton(
            text=emoji.emojize('HIGHPRICE  :zany_face:'),
            callback_data='/highprice'),
        types.InlineKeyboardButton(
            text=emoji.emojize('BESTDEAL   :partying_face:'),
            callback_data='/bestdeal'),
        types.InlineKeyboardButton(
            text=emoji.emojize('HISTORY   :brain:'),
            callback_data='/history')
    )
    result = my_bot.send_message(
        chat_id=message.chat.id,
        text='*Для выбора самых дешевых отелей выберите "lowprice"\n\n*'
             '*Для выбора самых дорогих отелей выберите "highprice"\n\n*'
             '*Для выбора отелей, наиболее подходящих по цене\n*'
             '*и расположению от центра горда выберите "bestdeal"\n\n*'
             '*Для отображения истории поиска выберите "history"*',
        reply_markup=keyboard, parse_mode='Markdown'
    )

    handlers.delete_prev_message(message)
    current_user.clear_all()
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


def yes_no_keyboard(message: types.Message) -> None:
    """Inline keyboard with answers a question about view photo of hotels.
    The id of the message with the on-screen
    keyboard is recorded in a special field of the User class (also the flag field
    is activated), for its further deletion (if necessary)

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text=emoji.emojize('ДА   :thumbs_up:'),
            callback_data='ДА'),
        types.InlineKeyboardButton(
            text=emoji.emojize('НЕТ   :thumbs_down:'),
            callback_data='НЕТ')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Хотите посмотреть фотографии отелей ?*',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


def menu_button() -> types.ReplyKeyboardMarkup:
    """Create menu button and return it

    :rtype: ReplyKeyboardMarkup"""

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False,
                                         resize_keyboard=True)
    keyboard.add(types.KeyboardButton(
        emoji.emojize('Меню   :desert_island:'))
    )
    return keyboard


def date_selection(message: types.Message) -> None:
    """Сreates a calendar for entering the check-in and
    check-out dates from the hotel. The id of the message with the on-screen
    keyboard is recorded in a special field of the User class (also the flag field
    is activated), for its further deletion (if necessary)

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    calendar, step = MyTranslationCalendar(locale='ru').build()
    result = my_bot.send_message(message.chat.id,
                                 f"Введите {MyTranslationCalendar.my_LSTEP[step]}",
                                 reply_markup=calendar)
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True


def cities_keyboard(message: types.Message) -> None:
    """Keyboard with the found  cities (state 1).
    The id of the message with the inline keyboard is recorded in a special field
    of the User class (also the flags field is activated): 1 - for its further deletion
     (if necessary) 2 - for going  to the next function after selecting the city.
     The current state of the bot is changed.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    keyboard = types.InlineKeyboardMarkup()
    for i_elem in current_user.current_buffer:
        for key, value in i_elem.items():
            keyboard.add(types.InlineKeyboardButton(text=key, callback_data=value))

    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Вот, что я нашел)*', reply_markup=keyboard,
                                 parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.zero_condition = False
    current_user.first_condition = True


def visit_the_website(message: types.Message) -> types.InlineKeyboardMarkup:
    """Creates a keyboard with a single button that opens the hotel's website

    :param message: argument
    :type message: Message object
    :return: keyboard
    :rtype: types.InlineKeyboardMarkup"""

    current_user = User.get_user(message.chat.id)
    button = types.InlineKeyboardButton(
        text='Сайт отеля',
        url=f'https://ru.hotels.com/ho{current_user.hotel_id}'
    )
    keyboard = types.InlineKeyboardMarkup().add(button)
    return keyboard


def show_more_hotels_part_1(message: types.Message) -> None:
    """After the first display of the specified number of hotels, it offers to load
    more hotels with the same parameters, start a new search or stop the search.
    The id of the inline keyboard is recorded for later deletion. The current state
    of the bot is changed. The flag is activated for the correct display of this particular
    inline keyboard when the user enters any messages or commands /hello-world
    and /help

     :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text=emoji.emojize('Еще отели   :grinning_face_with_big_eyes:'),
            callback_data='Загрузить еще отели'),
        types.InlineKeyboardButton(
            text=emoji.emojize('Новый поиск   :star-struck:'),
            callback_data='Новый поиск'),
        types.InlineKeyboardButton(
            text=emoji.emojize('Закончить   :face_with_spiral_eyes:'),
            callback_data='Закончить поиск')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Хотите продолжить просмотр отелей *'
                             '* с теми же параметрами? *',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.fourth_condition = False
    current_user.fifth_condition = True
    current_user.start_from_the_beginning_part_1 = True


def show_more_hotels_part_2(message: types.Message) -> None:
    """Suggests starting a new search or ending the search when there
    are no more hotels by the specified parameter. The id of the inline keyboard
    is recorded for later deletion. The flag is activated for the correct display
    of this particular inline keyboard when the user enters any messages
    or commands /hello-world and /help

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text=emoji.emojize('Новый поиск   :star-struck:'),
            callback_data='Новый поиск'),
        types.InlineKeyboardButton(
            text=emoji.emojize('Закончить поиск   :face_with_spiral_eyes:'),
            callback_data='Закончить поиск')
    )
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Больше по по вашему запросу ничего не найдено.*'
                             '* Хотите поискать новые отели?*',
                        parse_mode='Markdown')
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Я с удовольствием вам их покажу)*',
                                 reply_markup=keyboard, parse_mode='Markdown')
    current_user.id_message_for_delete = result.message_id
    current_user.delete_message = True
    current_user.start_from_the_beginning_part_1 = False
    current_user.start_from_the_beginning_part_2 = True
