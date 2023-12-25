from loader import bot
from telebot.types import Message
from database.bot_db import get_db
from handlers import help
from utils import decor_time


@bot.message_handler(commands=["history"])
@decor_time.chek_time
def get_history(m: Message) -> None:

    hotels_data = get_db(chat_id=m.chat.id)

    if hotels_data is not None:
        bot.reply_to(m, 'Результаты поиска, за все время:\n')
        for row in hotels_data:
            bot.send_message(m.from_user.id, text=f"Дата поиска отеля: {row[10]}\n"
                                                  f"Город поиска: {row[2]}\n"
                                                  f"Название отеля: {row[4]}\n"
                                                  f"Цена за сутки =  {row[5]} долларов США\n"
                                                  f"Стоимость за {int(row[8])} дней = {row[6]} долларов США\n"
                                                  f"Адрес отеля: {row[7]}\n"
                                                  f"Удаление от центра города = {row[9]} км\n")
    else:
        bot.reply_to(m, 'Пока нет истории поиска')

    help.bot_help(m)