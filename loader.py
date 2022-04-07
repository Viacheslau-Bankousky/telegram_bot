from dotenv import load_dotenv
import os
import telebot


load_dotenv(dotenv_path='.env')
my_bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


