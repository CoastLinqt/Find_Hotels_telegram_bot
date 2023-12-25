from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['hello-world'])
def hello_world(message: Message):
    bot.send_message(message.chat.id, text='Hello World!')