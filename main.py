from loader import my_bot
from telebot import types
from classes import MyTranslationCalendar, User, DetailedTelegramCalendar
from re import fullmatch
import handlers
import cmds_keyboard
import requests
import rapidapi


@my_bot.message_handler(commands=['start'])
def send_basic_greeting(message: types.Message) -> None:
    """Turns on the bot, calls its basic greeting and displays
    menu button

    :param message: argument
    :type message: Message object
    :return: None"""

    my_bot.send_message(message.from_user.id,
                        text='*Приветствую {}. Я Hotels_Searcher_bot *'
                             '* и я могу помочь вам найти  лучшие отели*'
                             '* на Hotels.com. Для того, чтобы просмотреть список*'
                             '* всего того, что я умею нажмите кнопу меню*'.format(
                            message.from_user.first_name),
                        reply_markup=cmds_keyboard.menu_button(),
                        parse_mode='Markdown')


@my_bot.message_handler(commands=['help'])
def help_me(message: types.Message) -> None:
    """Bot's reaction to the command /help. Calls a function that removes the
    previous built-in keyboard and displays it again after  displaying
    the message of the entered command

    :param message: argument
    :type message: Message object
    :return: None"""

    my_bot.send_message(chat_id=message.chat.id,
                        text='*Я с удовольствием помогу вам,*'
                             '* воспользуйтесь кнопкой меню, или продолжите начатое)*',
                        parse_mode='Markdown')

    handlers.check_condition_for_two_commands(message)


@my_bot.message_handler(commands=['hello-world'])
def say_hello_world(message: types.Message) -> None:
    """Bot's reaction to the command hello-world. Calls a function that removes
     the previous built-in keyboard and displays it again after  displaying
    the message of the entered command

    :param message: argument
    :type message: Message object
    :return: None"""

    my_bot.send_message(chat_id=message.chat.id,
                        text='*Да-да, и мир приветствует вас тоже)*',
                        parse_mode='Markdown')

    handlers.check_condition_for_two_commands(message)


@my_bot.message_handler(commands=['lowprice'])
def command_low_price(message: types.Message):
    """Displays a list of the cheapest hotels. The previous built-in keyboard is
    removed (if available), all dynamic attributes of the class object are updated.
    The current value of the entered command is set in a special attribute
    of the user class

     :param message: argument
     :type message: Message object
     :return: None"""

    current_user = User.get_user(message.chat.id)
    handlers.delete_prev_message(message)
    current_user.clear_all()
    current_user.current_command = '/lowprice'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем отели подешевле)*',
                        parse_mode='Markdown')
    handlers.initial_func(message)


@my_bot.message_handler(commands=['highprice'])
def command_high_price(message: types.Message):
    """Displays a list of the most expensive hotels. The previous built-in keyboard
     is removed (if available), all dynamic attributes of the class object are updated.
    The current value of the entered command is set in a special attribute
    of the user class

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    handlers.delete_prev_message(message)
    current_user.clear_all()
    current_user.current_command = '/highprice'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем отели подороже)*',
                        parse_mode='Markdown')
    handlers.initial_func(message)


@my_bot.message_handler(commands=['bestdeal'])
def cmd_best_deal(message: types.Message):
    """Displays a list of the most suitable hotels by price and distance
     from the city center. The previous built-in keyboard
     is removed (if available), all dynamic attributes of the class object are updated.
    The current value of the entered command is set in a special attribute
    of the user class

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    handlers.delete_prev_message(message)
    current_user.clear_all()
    current_user.current_command = '/bestdeal'
    my_bot.send_message(chat_id=message.chat.id,
                        text='*Что ж, поищем самые лучшие отели)*',
                        parse_mode='Markdown')
    handlers.initial_func(message)


@my_bot.message_handler(commands=['history'])
def command_history(message: types.Message):
    """Displays a list of all commands entered, the date and time of introduction,
    as well as their results. The previous built-in keyboard
    is removed (if available), all dynamic attributes of the class object are updated

    :param message: argument
    :type message: Message object
    :return: None"""

    pass


@my_bot.message_handler(content_types=['text'])
def send_return_greeting(message: types.Message) -> None:
    """ Depending on the current state of the bot, pressing the menu button
    reacts to any message entered by the user (and calls the corresponding
    function iif necessary, or offers the user to change their decision),
    deletes the previous inline keyboard (if it was already displayed earlier)
    and outputs it again after the bot's response.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if current_user.zero_condition:
        if message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
            cmds_keyboard.commands_keyboard(message)
        elif message.text in ('привет'.lower(), 'привет'.upper(), 'привет'.capitalize()):
            my_bot.send_message(chat_id=message.chat.id,
                                text="*Я к вашим услугам) *",
                                parse_mode='Markdown')
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Для быстрого получения результата лучше*'
                                     '* воспользуйтесь кнопкой меню или продолжите*'
                                     '* начатое )*',
                                parse_mode='Markdown')
    elif current_user.first_condition:
        if message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
            cmds_keyboard.commands_keyboard(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Если вы запутались, то начните с начала и*'
                                     '* нажмите на кнопку меню, либо продолжите начатое*'
                                     '* и сделайте выбор)*',
                                parse_mode='Markdown')
            handlers.delete_prev_message(message)
            cmds_keyboard.cities_keyboard(message)
    elif current_user.second_condition:
        if message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
            cmds_keyboard.commands_keyboard(message)
        elif fullmatch(r'\d{1,2}.\d{1,2}.\d{4}', message.text):
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Будет удобнее, если вы*'
                                     '* введете дату заселения*'
                                     '* при помощи клавиатуры на экране)*',
                                parse_mode='Markdown')
            handlers.delete_prev_message(message)
            cmds_keyboard.date_selection(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Я не устану предлагать вам воспользоваться *'
                                     '* кнопкой меню или продолжить начатое)*',
                                parse_mode='Markdown')
            handlers.delete_prev_message(message)
            cmds_keyboard.date_selection(message)
    elif current_user.fourth_condition:
        if message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
            cmds_keyboard.commands_keyboard(message)
        elif message.text in ('да'.lower(), 'да'.upper(), 'да'.capitalize()):
            handlers.delete_prev_message(message)
            handlers.yes_answer_about_foto(message)
        elif message.text in ('нет'.lower(), 'нет'.upper(), 'нет'.capitalize()):
            handlers.delete_prev_message(message)
            handlers.no_answer_about_foto(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Если что-то не понятно, всегда лучше *'
                                     '* начать с начала. Воспользуйтесь кнопкой меню*'
                                     '* или примите решение) *',
                                parse_mode='Markdown')
            handlers.delete_prev_message(message)
            cmds_keyboard.yes_no_keyboard(message)
    elif current_user.fifth_condition:
        if message.text == cmds_keyboard.emoji.emojize('Меню   :desert_island:'):
            cmds_keyboard.commands_keyboard(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Кажется вы утомились под конец, лучше *'
                                     '* начните с начала. Воспользуйтесь кнопкой меню*'
                                     '* или продолжите начатое и нажмите на одну из кнопок) *',
                                parse_mode='Markdown')
            if current_user.start_from_the_beginning_part_1:
                handlers.delete_prev_message(message)
                cmds_keyboard.show_more_hotels_part_1(message)
            elif current_user.start_from_the_beginning_part_2:
                handlers.delete_prev_message(message)
                cmds_keyboard.show_more_hotels_part_2(message)


@my_bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def first_query_handler(call: types.CallbackQuery) -> None:
    """Handles callback queries when calendar buttons are pressed
    and calls the corresponding custom handlers  (check-in and check_out)
    The appropriate function from handlers is selected using a
     special date_flag of the user class. The entered date is recorded in a special
     attribute-buffer for later use in functions check_in and check_out

    :param call: argument
    :type call: CallbackQuery object
    :return: None"""

    result, key, step = MyTranslationCalendar(locale='ru').process(call.data)
    if not result and key:
        my_bot.edit_message_text(
            f"Выберите {MyTranslationCalendar.my_LSTEP[step]}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=key
        )
    elif result:
        current_user = User.get_user(call.message.chat.id)
        current_user.date_buffer = result
        my_bot.edit_message_text(f"*Вы ввели {result.strftime('%d.%m.%Y')}*",
                                 chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 parse_mode='Markdown')
        if current_user.date_flag is False:
            handlers.check_in(call.message)
        else:
            handlers.check_out(call.message)


@my_bot.callback_query_handler(func=lambda call: True)
def second_query_handler(call: types.CallbackQuery) -> None:
    """Handles callback queries pressed inline buttons keyboard (commands,
    response about viewing photos, buttons with hotels, offer further viewing
    of hotels with the same parameters, a new search or completion of the search
     after the first display of the found hotels) and calls the appropriate functions.
    The previous inline keyboard is removed if necessary

    :param call: argument
    :type call: CallbackQuery object
    :return: None"""

    current_user = User.get_user(call.message.chat.id)

    if call.data == '/bestdeal':
        my_bot.answer_callback_query(callback_query_id=call.id)
        cmd_best_deal(call.message)
    elif call.data == '/lowprice':
        my_bot.answer_callback_query(callback_query_id=call.id)
        command_low_price(call.message)
    elif call.data == '/highprice':
        my_bot.answer_callback_query(callback_query_id=call.id)
        command_high_price(call.message)
    elif call.data == '/history':
        pass
    elif call.data == 'ДА':
        my_bot.answer_callback_query(callback_query_id=call.id)
        my_bot.send_message(chat_id=call.message.chat.id, text=call.data)
        current_user.answer_about_photo = call.data
        handlers.yes_answer_about_foto(call.message)
    elif call.data == 'НЕТ':
        my_bot.answer_callback_query(callback_query_id=call.id)
        my_bot.send_message(chat_id=call.message.chat.id, text=call.data)
        current_user.answer_about_photo = call.data
        handlers.no_answer_about_foto(call.message)
    elif call.data == 'Загрузить еще отели':
        my_bot.answer_callback_query(callback_query_id=call.id)
        my_bot.send_message(chat_id=call.message.chat.id, text=call.data)
        handlers.delete_prev_message(call.message)
        rapidapi.delete_showed_hotels(call.message)
    elif call.data == 'Новый поиск':
        my_bot.answer_callback_query(callback_query_id=call.id)
        my_bot.send_message(chat_id=call.message.chat.id, text=call.data)
        cmds_keyboard.commands_keyboard(call.message)
    elif call.data == 'Закончить поиск':
        my_bot.answer_callback_query(callback_query_id=call.id)
        my_bot.send_message(chat_id=call.message.chat.id, text=call.data)
        handlers.delete_prev_message(call.message)
        my_bot.send_message(chat_id=call.message.chat.id,
                            text='*Спасибо, что выбрали меня. Обращайтесь снова*'
                                 '* при любой необходимости)*',
                            parse_mode='Markdown')
        current_user.clear_all()
    else:
        for i_elem in current_user.current_buffer:
            for key, value in i_elem.items():
                if call.data == value:
                    my_bot.answer_callback_query(callback_query_id=call.id)
                    my_bot.send_message(chat_id=call.message.chat.id,
                                        text=f'Хорошо, я запомню ваш выбор: {key}')
                    current_user.destination_id = value
                    handlers.delete_prev_message(call.message)
                    handlers.differance_between_commands(call.message)
                break


def main() -> None:
    """The bot's endless appeal to the Telegram server in order to check
    for new messages

    :rtype: None"""

    try:
        my_bot.infinity_polling(timeout=0)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout):
        pass


if __name__ == '__main__':
    main()
