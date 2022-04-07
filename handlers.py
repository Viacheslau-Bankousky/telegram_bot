import rapidapi
from main import command_low_price, command_high_price, cmd_best_deal
from main import say_hello_world, help_me, command_history
from loader import my_bot
from classes import User
from datetime import date
from telebot import types
from rapidapi import request_to_api
import cmds_keyboard


def initial_func(message: types.Message) -> None:
    """""The initial handler of the user's message, offering
    to select the city in which the hotel will be searched, writes the name of next 
    function in the corresponding field of the data class directing
    response to the command input validation handler

    :param message: argument
    :type message: Message object
    :return: None"""""

    current_user = User.get_user(message.chat.id)

    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Теперь выберите город, для поиска отеля  *',
                                 parse_mode='Markdown')
    current_user.next_func = determ_city
    my_bot.register_next_step_handler(result, check_message)


def determ_city(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the selected city) and offers to re-enter if its format
    specified incorrectly; if the message format is specified correctly
     it displays the hotels via the API request function

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isalpha() or [letter for letter in message.text
                                  if letter.isspace() or letter.isalpha()]:
        current_user.city = message.text.lower()
        result_waiting(message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '*Попробуйте еще раз указать название города *',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def differance_between_commands(message: types.Message) -> None:
    """Depending on the initial commands,
    it offers to choose either the desired number of hotels
    (when entering lowprice and highprice), or the minimum cost
    per day of stay in it (when entering the best deal). The name of the
    following function is written in a special field of the data class.
    The message is sent to the command input verification function.
    The current state of the bot is changed.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    current_user.first_condition = False
    current_user.second_condition = True
    if current_user.current_command in ('/lowprice', '/highprice'):
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*А сейчас выберите количество отелей*',
                                     parse_mode='Markdown')
        current_user.next_func = hotels_count
        my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Введите минимальную цену*'
                                          '* за сутки в отеле*',
                                     parse_mode='Markdown')
        current_user.next_func = min_price
        my_bot.register_next_step_handler(result, check_message)


def min_price(message: types.Message) -> None:
    """The handler that interacts with the entered
    the message (the minimum cost of the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    offers to specify the maximum cost per night of staying at the hotel.
    The name of the following function is written in a special field of the data class.
    The message is sent to the command input verification function.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if int(message.text) > 0:
            current_user.min_price = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Введите максимальную цену*'
                                              '* за сутки проживания в отеле*',
                                         parse_mode='Markdown')
            current_user.next_func = max_price
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы введи не допустимую сумму.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другую сумму*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def max_price(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the maximum cost of the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    suggests specifying the minimum distance of the hotel from the city center.
    The name of the following function is written in a special field of the data class.
    The message is sent to the command input verification function.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if 0 < int(message.text) > current_user.min_price:
            current_user.max_price = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Введите минимальное расстояние *'
                                              '*от отеля до центра города (в км)*',
                                         parse_mode='Markdown')
            current_user.next_func = min_distance
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели  сумму, которая меньше*'
                                              '* указанной первоначально.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другую сумму*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def min_distance(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the minimum distance of the hotel from the city center) and
    offers to re-enter if its format is specified incorrectly.
    If the correct message is entered, it offers to specify
    the maximum distance of the hotel from the city center.
    The name of the following function is written in a special field of the data class.
    Message it is sent to the command input verification function.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if int(message.text) > 0:
            current_user.min_distance = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Введите максимальное расстояние *'
                                              '* от отеля до центра города (в км)*',
                                         parse_mode='Markdown')
            current_user.next_func = max_distance
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели не допустимое расстояние.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другое расстояние*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def max_distance(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the maximum distance from the city center) and
    offers to enter it again if its format is specified incorrectly.
    If the correct message is entered, it offers to specify
    the displayed number of hotels.
    The name of the following function is written in a special field of the data class.
    The message is sent to the command input verification function.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if 0 < int(message.text) > current_user.min_distance:
            current_user.max_distance = int(message.text)
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Теперь выберите количество отелей,*'
                                              '* которое хотите посмотреть *',
                                         parse_mode='Markdown')
            current_user.next_func = hotels_count
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели  расстояние, которое меньше*'
                                              '* указанного первоначально.*'
                                              '* Попробуйте еще раз*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Попробуйте ввести другое расстояние*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def hotels_count(message: types.Message) -> None:
    """The handler that interacts with the entered
    message (number of hotels) and offers to re-enter,
    if its format is specified incorrectly. If the message format is correct,
    it is suggested to indicate the number of adults who are going to check
    into the hotel. The name of the following function is written in a special field
    of the data class. The message is sent to the command input verification function.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if 0 < int(message.text) < 6:
            current_user.hotels_count = int(message.text)
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Хорошо, я запомню)*',
                                parse_mode='Markdown')
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Какое количество взрослых планируют*'
                                              '* проживать в отеле?*',
                                         parse_mode='Markdown')
            current_user.next_func = adults_count
            my_bot.register_next_step_handler(result, check_message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели не допустимое количество отелей.*'
                                              '* Для удобного отображения на экране лучше *'
                                              '* выбрать от 1 до 5. Попробуйте еще раз)*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '* Попробуйте еще раз указать количество отелей*'
                                          '* используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def adults_count(message: types.Message) -> None:
    """The handler that interacts with the entered
    message (number of adults checking into the hotel) and offers to re-enter,
    if its format is specified incorrectly. If the correct message is entered,
    offers select the check-in date at the hotel. The current state of the bot
    is changing

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    if message.text.isdigit():
        current_user.adults_count = message.text
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Хорошо я запомню)*'
                                 '* Теперь выберите  дату заселения*',
                            parse_mode='Markdown')
        cmds_keyboard.date_selection(message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо) *'
                                          '* Попробуйте еще раз указать количество*'
                                          '* людей, которые будут заселяться в отель,*'
                                          '* используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def yes_answer_about_foto(message: types.Message) -> None:
    """The handler of a command, responding to a positive response, a question
    about displaying photos of the hotel and calling the function of selecting them
    quantities. Initially the name of the following function is written in a special field
    of the data class. The message is sent to the command input verification function.
    Emoji from result_waiting is forcibly deleted.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    delete_prev_message(message)
    result = my_bot.send_message(chat_id=message.chat.id,
                                 text='*Какое количество фотографий *'
                                      '* хотите  отобразить на экране? *',
                                 parse_mode='Markdown')
    current_user.next_func = photo_count
    my_bot.register_next_step_handler(result, check_message)


def no_answer_about_foto(message: types.Message) -> None:
    """The handler of the command, responding to a negative response, question
    about displaying hotel photos.  Emoji from result_waiting is forcibly deleted.

    :param message: argument
    :type message: Message object
    :return: None"""

    delete_prev_message(message)
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Значит будем без фотографий) *',
                        parse_mode='Markdown')
    rapidapi.result_displaying(message)


def photo_count(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the number of displayed photos of the hotel) and
    offers to re-enter if its format is specified incorrectly.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text.isdigit():
        if 0 < int(message.text) < 11:
            current_user.photo_count = int(message.text)
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Хорошо я запомню)*',
                                parse_mode='Markdown')
            rapidapi.result_displaying(message)
        else:
            result = my_bot.send_message(chat_id=message.chat.id,
                                         text='*Вы ввели не допустимое количество*'
                                              '* фотографий. Для удобного просмотра*'
                                              '* выберите от 1 до 10*',
                                         parse_mode='Markdown')
            my_bot.register_next_step_handler(result, check_message)
    else:
        result = my_bot.send_message(chat_id=message.chat.id,
                                     text='*Кажется вы ввели не совсем то, что надо. *'
                                          '* Попробуйте ввести еще раз необходимое *'
                                          '* количество фото, используя только цифры*',
                                     parse_mode='Markdown')
        my_bot.register_next_step_handler(result, check_message)


def check_in(message: types.Message) -> None:
    """The handler that interacts with the entered
    a message (the date of check-in at the hotel) and offers to re-enter,
    if it is specified incorrectly. If the correct message is entered,
    the question is asked about the date on which the accommodation is planned
    In a hotel. The date_flag attribute of the user class object determines the priority
    of calling the check_in and check_out functions. The entered date is taken
    from a special buffer attribute

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if not str(current_user.date_buffer - date.today()).startswith('-'):
        current_user.check_in = current_user.date_buffer
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Выберите дату, до которой планируете *'
                                 '*проживать в отеле*',
                            parse_mode='Markdown')
        current_user.date_flag = True
        cmds_keyboard.date_selection(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Была указана дата из прошлого.*'
                                 '* Попробуйте еще раз*',
                            parse_mode='Markdown')
        cmds_keyboard.date_selection(message)


def check_out(message: types.Message) -> None:
    """The handler that interacts with the entered message
    (the date on which you plan to stay at the hotel) and
    offers to enter it again if it is specified incorrectly. The entered date is taken
    from a special buffer attribute. If the correct message is entered,
    the API request function is called. The current state of the bot is changed.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if not str(current_user.date_buffer - date.today()).startswith('-'):
        if not str(current_user.date_buffer - current_user.check_in).startswith('-'):
            current_user.check_out = current_user.date_buffer
            current_user.second_condition = False
            current_user.third_condition = True
            result_waiting(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='* Указана не допустимая дата *'
                                     '* (меньше даты заселения). *'
                                     '* Попробуйте еще раз*',
                                parse_mode='Markdown')
            cmds_keyboard.date_selection(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Была указана дата из прошлого.*'
                                 '* Попробуйте еще раз*',
                            parse_mode='Markdown')
        cmds_keyboard.date_selection(message)


def check_message(message: types.Message) -> None:
    """Checks whether the entered messages correspond to the main ones
    commands of the bot or causes a response to the pressed
    menu button. Redirection to the corresponding function is carried out with
    a positive result or transition to the next stage of the scenario
    (the next_function attribute of the user class object is used). if the /help and
    /hello-world commands are entered, after calling them, the validator function
    is called again (because these 2 commands do not play a special role in
    the further logic of the bot)

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text == '/lowprice':
        command_low_price(message)
    elif message.text == '/highprice':
        command_high_price(message)
    elif message.text == '/bestdeal':
        cmd_best_deal(message)
    elif message.text == '/history':
        pass
    elif message.text == '/hello-world':
        say_hello_world(message)
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Теперь можете продолжить с предыдущего шага *'
                                 '* и ввести то, что не успели*', parse_mode='Markdown')
        my_bot.register_next_step_handler(message, check_message)
    elif message.text == '/help':
        help_me(message)
        my_bot.register_next_step_handler(message, check_message)
    elif message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
        cmds_keyboard.commands_keyboard(message)
    else:
        current_user.next_func(message)


def delete_prev_message(message: types.Message) -> None:
    """Removes the previous built-in buttons or message if it is possible
    and necessary

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    try:
        if current_user.delete_message is True:
            my_bot.delete_message(chat_id=message.chat.id,
                                  message_id=current_user.id_message_for_delete)
            current_user.delete_message = False
    except Exception:
        pass


def check_condition_for_two_commands(message: types.Message) -> None:
    """Depending on the current state, it removes either the inline keyboard
    with variants of found cities,  question about viewing photos, the  calendar
    or suggestion to continue or end the search (in the end of the script),
    and then displays them again below the entered message (necessary for
    the /help and /hello-world command entered in the corresponding state
    of the bot)

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    delete_prev_message(message)
    if current_user.first_condition:
        cmds_keyboard.cities_keyboard(message)
    elif current_user.second_condition:
        cmds_keyboard.date_selection(message)
    elif current_user.fourth_condition:
        cmds_keyboard.yes_no_keyboard(message)
    elif current_user.fifth_condition:
        if current_user.start_from_the_beginning_part_1:
            cmds_keyboard.show_more_hotels_part_1(message)
        elif current_user.start_from_the_beginning_part_2:
            cmds_keyboard.show_more_hotels_part_2(message)


def result_waiting(message: types.Message):
    """It displays waiting message and gif-image, and after receiving
    a response from the API, deletes them. Depending on the current state
    of the bot, it calls the corresponding function, or does the same and
    changes the state. The id if message is recorded for subsequent forced
    deletion after calling the keyboard with a question about viewing the photo

     :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    first_result = my_bot.send_message(chat_id=message.chat.id,
                                       text='*Выполняю поиск. Подождите немного*',
                                       parse_mode='Markdown')

    second_result = my_bot.send_video(message.chat.id,
                                      'https://i.gifer.com/FWcb.gif', None, 'Text')
    current_user.id_message_for_delete = second_result.message_id
    current_user.delete_message = True

    if request_to_api(message):
        if current_user.fourth_condition or current_user.fifth_condition:
            rapidapi.photo_selection(message)
        if current_user.third_condition:
            current_user.third_condition = False
            current_user.fourth_condition = True
            cmds_keyboard.yes_no_keyboard(message)
        my_bot.delete_message(chat_id=message.chat.id,
                              message_id=second_result.message_id)
        my_bot.delete_message(chat_id=message.chat.id,
                              message_id=first_result.message_id)
