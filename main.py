from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio
import config

my_bot = AsyncTeleBot(config.token)


@my_bot.message_handler(commands=['start'])
async def send_basic_greeting(message: types.Message) -> None:
    """Метод включает бота и вызывает базовое приветствие

     :param message: argument
     :type message: Message object
     :return: None"""

    await my_bot.send_message(
        message.chat.id, 'Приветствую {} чем могу помочь?'.format(
            message.from_user.first_name)
    )


@my_bot.message_handler(commands=['help'])
async def help_me(message: types.Message) -> None:
    """Метод выводит список доступных команд бота

     :param message: argument
     :type message: Message object
     :return: None"""

    with open('list of commands', 'r', encoding='utf-8') as file:
        await my_bot.send_message(message.chat.id, file.read())


@my_bot.message_handler(commands=['hello-world'])
async def say_hello_world(message: types.Message) -> None:
    """Метод вызывает реакцию бота на команду hello-world

     :param message: argument
     :type message: Message object
     :return: None"""

    await my_bot.send_message(
        message.chat.id, 'Привет мир!'
    )


@my_bot.message_handler(content_types=['text'])
async def send_return_greeting(message: types.Message) -> None:
    """Метод вызывает реакцию бота при вводе пользователем ''привет''
     в любом регистре или предлагает воспользоваться командой /help если
     бот не распознал введенное сообщение

      :param message: argument
     :type message: Message object
     :return: None"""

    if message.text in ('привет'.lower(), 'привет'.upper(), 'привет'.capitalize()):
        await my_bot.send_message(
            message.chat.id,
            """Я к вашим услугам) Ищите хороший отель?"""
        )
    else:
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='help', callback_data='help'))
        await my_bot.send_message(
            message.chat.id,
            'Кажется вам нужна моя помощь) '
            'Чтобы посмотреть список всех доступных команд '
            'нажмите нижнюю кнопку',
            reply_markup=keyboard
        )


@my_bot.callback_query_handler(func=lambda call: True)
async def query_handler(call: types.CallbackQuery) -> None:
    """Метод обрабатывает обратные вызовы и при соответствии их данных
     заданному параметру, вызывает соответствующий метод

     :param call: argument
     :type call: CallbackQuery object
     :return: None"""

    if call.data == 'help':
        await my_bot.answer_callback_query(callback_query_id=call.id)
        await help_me(call.message)
        await my_bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id)


if __name__ == '__main__':
    asyncio.run(my_bot.infinity_polling(timeout=0))
