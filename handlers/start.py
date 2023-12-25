from telebot.types import Message
from loader import bot
from utils import decor_time
import emoji


@bot.message_handler(commands=["start"])
@decor_time.chek_time
def bot_start(m: Message):
    """Запуск бота и приветствие"""

    bot.reply_to(m, f"Здравствуйте, {m.from_user.full_name} {emoji.emojize('👋')}! Данный бот поможет с выбором лучших отелей и цен по всему миру.\n "
                    f"Для того, чтобы обратиться к боту и узнать его возможности, нажмите {emoji.emojize('➡')} /help")