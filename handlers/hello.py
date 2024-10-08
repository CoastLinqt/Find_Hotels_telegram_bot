from loader import bot
from telebot.types import Message


@bot.message_handler(state=None, content_types='text')
def hello_message(message: Message) -> None:
    """Ответ пользователю на сообщение привет"""
    if message.text.lower() == 'привет':
        bot.reply_to(message, f"Приветствую, {message.from_user.full_name}!")