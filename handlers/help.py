from telebot.types import Message
from loader import bot
from utils import decor_time


@bot.message_handler(commands=["help"])
@decor_time.chek_time
def bot_help(m: Message):

    text = "/help — помощь по командам бота.\n" \
           "/lowprice — вывод самых дешёвых отелей в городе.\n" \
           "/custom — вывод отелей, наиболее подходящих по цене.\n" \
           "/history — вывод истории поиска отелей.\n"
    bot.send_message(m.chat.id, text, parse_mode='html')
