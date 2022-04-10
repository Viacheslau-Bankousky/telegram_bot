from re import fullmatch
from loader import my_bot
from telebot.types import Message
from classes.data_class import User
import keyboards.inline.inline_keyboards as inline
import emoji
import handlers.handlers_before_request.handlers as handlers


def send_greeting(message: Message) -> None:
    """Reacts to the pressed menu button, the hello message entered by the user,
     or offers to use the menu button for any other message

     :param message: argument
    :type message: Message object
    :return: None"""

    if message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
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


def send_initial_answer(message: Message) -> None:
    """Reacts to the pressed menu button or offers to use it if any message
     is entered (in this case, the previous inline keyboard with the displayed hotels
    is deleted and displayed again after the bot's response)

    :param message: argument
    :type message: Message object
    :return: None """

    if message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Если вы запутались, то начните с начала и*'
                                 '* нажмите на кнопку меню, либо продолжите начатое*'
                                 '* и сделайте выбор)*',
                            parse_mode='Markdown')
        handlers.delete_previous_message(message)
        inline.cities_keyboard(message)


def send_middle_answer(message: Message) -> None:
    """Reacts to the pressed menu button. If the user has entered a message
    in the form of a date, the bot offers to use an inline calendar. If any other
    message is entered, it suggests using the menu button. In all cases,
    the previous inline keyboard with the calendar is deleted and displayed
    again after the bot's response

    :param message: argument
    :type message: Message object
    :return: None"""

    if message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
    elif fullmatch(r'\d{1,2}.\d{1,2}.\d{4}', message.text):
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Будет удобнее, если вы*'
                                 '* введете дату заселения*'
                                 '* при помощи клавиатуры на экране)*',
                            parse_mode='Markdown')
        handlers.delete_previous_message(message)
        inline.date_selection(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Я не устану предлагать вам воспользоваться *'
                                 '* кнопкой меню или продолжить начатое)*',
                            parse_mode='Markdown')
        handlers.delete_previous_message(message)
        inline.date_selection(message)


def send_next_middle_answer(message: Message) -> None:
    """Reacts to the pressed menu button. If the user, when asked about
    viewing photos, instead of using the built-in keyboard, manually enter
    yes or no, calls the corresponding function from the handlers and deletes
    the previous inline keyboard. When user entered any other message,
    the inline keyboard with a question about viewing hotel photos is deleted
    and displayed again after the bot responds

    :param message: argument
    :type message: Message object
    :return: None"""

    if message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
    elif message.text in ('да'.lower(), 'да'.upper(), 'да'.capitalize()):
        handlers.delete_previous_message(message)
        handlers.yes_answer_about_photo(message)
    elif message.text in ('нет'.lower(), 'нет'.upper(), 'нет'.capitalize()):
        handlers.delete_previous_message(message)
        handlers.no_answer_about_photo(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Если что-то не понятно, всегда лучше *'
                                 '* начать с начала. Воспользуйтесь кнопкой меню*'
                                 '* или примите решение) *',
                            parse_mode='Markdown')
        handlers.delete_previous_message(message)
        inline.yes_no_keyboard(message)


def send_last_answer(message: Message) -> None:
    """Reacts to the pressed menu button or offers to use it when entering
    any message. If there are still available hotels, displays an inline keyboard
    with a suggestion to download more, start a new search or start a search.
    If there are no more available hotels, displays the inline keyboard with
    a suggestion to start new searching or end the search

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)

    if message.text == emoji.emojize('Меню   :desert_island:'):
        inline.commands_keyboard(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Кажется вы утомились под конец, лучше *'
                                 '* начните с начала. Воспользуйтесь кнопкой меню*'
                                 '* или продолжите начатое и нажмите на одну из кнопок) *',
                            parse_mode='Markdown')
        if current_user.start_from_the_beginning_part_1:
            handlers.delete_previous_message(message)
            inline.show_more_hotels_part_1(message)
        elif current_user.start_from_the_beginning_part_2:
            handlers.delete_previous_message(message)
            inline.show_more_hotels_part_2(message)
