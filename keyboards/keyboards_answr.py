from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Dict
from loader import bot
from telebot import types
import emoji


def city_keyboard(m: Message, city_dict: Dict):
    buttons = InlineKeyboardMarkup()
    if not city_dict:
        bot.reply_to(m, f"Такого города не удалось найти{emoji.emojize('☹')}. Повторите запрос /help")
    else:
        for k, v in city_dict.items():
            buttons.add(InlineKeyboardButton(text=k, callback_data=str(v)))
        bot.send_message(m.from_user.id, "Уточните, пожалуйста, нажав нужную клавишу",
                         reply_markup=buttons)
    return buttons


def yes_no():
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Да', callback_data='да')
    item2 = types.InlineKeyboardButton('Нет', callback_data='нет')
    return markup.add(item, item2)


def hotel_qty():
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('1', callback_data='1')
    item2 = types.InlineKeyboardButton('2', callback_data='2')
    item3 = types.InlineKeyboardButton('3', callback_data='3')
    item4 = types.InlineKeyboardButton('4', callback_data='4')
    item5 = types.InlineKeyboardButton('5', callback_data='5')

    return markup.add(item, item2, item3, item4, item5)


def photo_qty():
    markup = types.InlineKeyboardMarkup(row_width=3)
    item = types.InlineKeyboardButton('1', callback_data='1')
    item2 = types.InlineKeyboardButton('2', callback_data='2')
    item3 = types.InlineKeyboardButton('3', callback_data='3')
    return markup.add(item, item2, item3)


def min_price():
    markup = types.InlineKeyboardMarkup(row_width=3)
    item = types.InlineKeyboardButton('10$', callback_data='10')
    item2 = types.InlineKeyboardButton('70$', callback_data='70')
    item3 = types.InlineKeyboardButton('130$', callback_data='130')
    item4 = types.InlineKeyboardButton('200$', callback_data='200')
    item5 = types.InlineKeyboardButton('260$', callback_data='260')
    item6 = types.InlineKeyboardButton('Выбрать', callback_data='выбор')
    return markup.add(item, item2, item3, item4, item5, item6)


def max_price():
    markup = types.InlineKeyboardMarkup(row_width=3)
    item = types.InlineKeyboardButton('40$', callback_data='40')
    item2 = types.InlineKeyboardButton('100$', callback_data='100')
    item3 = types.InlineKeyboardButton('170$', callback_data='170')
    item4 = types.InlineKeyboardButton('230$', callback_data='230')
    item5 = types.InlineKeyboardButton('290$', callback_data='290')
    item6 = types.InlineKeyboardButton('Выбрать', callback_data='выбор')
    return markup.add(item, item2, item3, item4, item5, item6)