from loader import bot


@bot.message_handler(state=None, content_types=['text'])
def bot_echo(message):
    bot.reply_to(message, f"{message.text}")