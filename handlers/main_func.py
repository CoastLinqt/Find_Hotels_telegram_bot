from telebot.types import Message, CallbackQuery
from loader import bot
from states.states_bot import States
import datetime
import emoji

from handlers.request_API import city_request, get_hotel_list, get_hotel_details
from keyboards import keyboards_answr
from telegram_bot_calendar import DetailedTelegramCalendar
from database.bot_db import add_response_to_db
from utils import decor_time


LSTEP: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(commands=["lowprice", "custom"])
@decor_time.chek_time
def main_function(message: Message) -> None:
    """Функция обрабатывает запросы /lowprice, /custom и
    ловит ответ пользователя - город для поиска отеля."""

    bot.set_state(message.from_user.id, States.city, message.chat.id)
    bot.send_message(message.from_user.id, text=f"Напишите, какой город Вас интересует(Текст на латинице){emoji.emojize('😊')}?\n\n"
                                          f"*Уважаемый пользователь, русские города в поиске отсутствуют.{emoji.emojize('😔')}")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1:]


@bot.message_handler(state=States.city)
@decor_time.chek_time
def get_city_name(message: Message) -> None:
    """Делается запрос к API и получение список городов"""
    city_name = message.text
    if not city_name.isdigit():
        city_data = city_request(city_name)
        keyboards_answr.city_keyboard(message, city_data)
        bot.set_state(message.from_user.id, States.city_id, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cities_data'] = city_data
    else:
        raise Exception(bot.reply_to(message, f"Ошибка в написании города. Должны быть только буквы. {emoji.emojize('🔤')}"))


@bot.callback_query_handler(func=None, state=States.city_id)
@decor_time.chek_time
def get_city_id(call: CallbackQuery):
    """Получение ID города и вопрос про кол-во отелей, записывание в состояние.
    Если изначальное состояние /custom, тогда переходим к выбору минимальной цены."""
    city_id = call.data
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        city_data = data['cities_data']
        command = data['command']
    city_name = ""
    for k, v in city_data.items():
        if city_id == v:
            city_name = k
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = city_name
        data['city_id'] = int(city_id)

    if command == 'custom':
        bot.send_message(
            call.from_user.id,
            f"Выберите минимальную стоимость или  нажмите на кнопку 'Выбрать' и напишите сумму самостоятельно.{emoji.emojize('💸')}"
            "\n\n*Стоимость отеля за ночь.", reply_markup=keyboards_answr.min_price()
        )
        bot.set_state(call.from_user.id, States.min_price, call.message.chat.id)

    else:
        bot.send_message(call.from_user.id, f"Отлично. Cколько отелей хотите просмотреть (не более 5)?{emoji.emojize('🏨')}", reply_markup=keyboards_answr.hotel_qty())
        bot.set_state(call.from_user.id, States.hotel_qty, call.message.chat.id)


@bot.callback_query_handler(func=None, state=States.min_price)
@decor_time.chek_time
def get_min_custom(call) -> None:
    """Функция на ввод максимальной цены. Записываем в состояние"""
    if call.message:
        if call.data == 'выбор':
            bot.send_message(
                call.from_user.id,
                f"Напишите минимальную стоимость.{emoji.emojize('💵')} ")
            bot.set_state(call.from_user.id, States.min_custom, call.message.chat.id)
        if call.data.isdigit():
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:

                min_price = call.data
                data['min_price'] = float(min_price)

            bot.send_message(
                call.from_user.id,
                f"Выберите максимальную стоимость или нажмите на кнопку 'Выбрать' и напишите сумму самостоятельно.{emoji.emojize('💸')}"
                "\n\n*Стоимость отеля за ночь.", reply_markup=keyboards_answr.max_price())
            bot.set_state(call.from_user.id, States.max_price, call.message.chat.id)

    else:
        raise Exception('-')


@bot.message_handler(state=States.min_custom)
@decor_time.chek_time
def price_min(m):
    """Функция срабатывает при нажатии кнопки 'Выбрать', записывает результат"""
    if m.text:
        if m.text.isdigit():
            bot.send_message(
                m.from_user.id,
                f"Выберите максимальную стоимость или нажмите на кнопку 'Выбрать' и напишите сумму самостоятельно.{emoji.emojize('💸')}"
                "\n\n*Стоимость отеля за ночь", reply_markup=keyboards_answr.max_price())
            bot.set_state(m.from_user.id, States.max_price, m.chat.id)
            with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
                data['min_price'] = float(m.text)
        else:
            bot.reply_to(m, "Ошибка. Только цифры.")


@bot.callback_query_handler(func=None, state=States.max_price)
@decor_time.chek_time
def get_max_price(call) -> None:
    """Функция запрашивает от пользователя для команды /custom, кол-во отелей."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:

        min_price = data['min_price']

    if call.message:
        if call.data == 'выбор':
            bot.send_message(
                call.from_user.id,
                f"Напишите максимальную сумму.{emoji.emojize('💵')} ")
            bot.set_state(call.from_user.id, States.max_custom, call.message.chat.id)
        if call.data.isdigit():
            max_price = float(call.data)
            if max_price >= min_price:
                bot.send_message(call.from_user.id, f"Отлично. Cколько отелей хотите просмотреть (не более 5)?{emoji.emojize('🏨')}", reply_markup=keyboards_answr.hotel_qty())
                bot.set_state(call.from_user.id, States.hotel_qty, call.message.chat.id)
                with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                    data['max_price'] = max_price
            else:
                raise Exception(bot.send_message(call.from_user.id, f"Ошибка. Максимальная цена должна быть больше минимальной.{emoji.emojize('🆘')}"))
    else:
        bot.send_message(call.from_user.id, f"Ошибка. Максимальная цена должна быть больше минимальной.{emoji.emojize('🆘')}")


@bot.message_handler(state=States.max_custom)
@decor_time.chek_time
def price_max(m):
    """Функция срабатывает при нажатии кнопки 'Выбрать', записывает результат"""
    with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
        min_price = data['min_price']
    if m.text:
        if m.text.isdigit():
            max_price = float(m.text)
            if max_price > min_price:
                bot.send_message(m.from_user.id, f"Отлично. Cколько отелей хотите просмотреть (не более 5)?{emoji.emojize('🏨')}",
                                 reply_markup=keyboards_answr.hotel_qty())
                bot.set_state(m.from_user.id, States.hotel_qty, m.chat.id)
                with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
                    data['max_price'] = max_price
            else:
                raise Exception(bot.reply_to(m, f"Ошибка. Максимальная цена должна быть больше минимальной.{emoji.emojize('🆘')}"))
        else:
            bot.reply_to(m, "Ошибка. Только цифры.")


@bot.callback_query_handler(func=None, state=States.hotel_qty)
@decor_time.chek_time
def get_photo(call) -> None:
    """Записываем кол-во отелей в состояние пользователя и задаём следующий вопрос"""

    if call.data.isdigit() and 0 < int(call.data) < 6:
        bot.send_message(call.from_user.id, f"Спасибо. Сколько фото показать (не более 3-х){emoji.emojize('🏞')}?", reply_markup=keyboards_answr.photo_qty())
        bot.set_state(call.from_user.id, States.photo_custom, call.message.chat.id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['hotel_qty'] = call.data
    else:
        raise Exception('-')


@bot.callback_query_handler(func=None, state=States.photo_custom)
@decor_time.chek_time
def set_photo(call):
    """Функция возвращает количество фото и записывает их."""
    if call.data.isdigit() and 0 < int(call.data) < 4:
        bot.set_state(call.from_user.id, States.photo, call.message.chat.id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['photo'] = int(call.data)
        bot.send_message(call.from_user.id, f"Теперь необходимо выбрать дату заезда.{emoji.emojize('📆')}")
        calendar_first, step = DetailedTelegramCalendar(calendar_id=1, locale='ru',
                                                        min_date=datetime.date.today()).build()
        bot.send_message(call.message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar_first)
        bot.set_state(call.from_user.id, States.check_in, call.message.chat.id)
    else:
        raise Exception('')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1), state=States.check_in)
@decor_time.chek_time
def calendar(call: CallbackQuery):
    """Ответ по календарю 1 для даты заезда"""
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата заезда{emoji.emojize('🔜')}: {result}",
                                call.message.chat.id,
                                call.message.message_id)
        bot.send_message(call.from_user.id, f"Теперь необходимо выберите дату выезда.{emoji.emojize('📆')}")

        calendar_second, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=result).build()
        bot.send_message(call.message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar_second)
        bot.set_state(call.from_user.id, States.check_out, call.message.chat.id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2), state=States.check_out)
@decor_time.chek_time
def calendar(call: CallbackQuery):
    """Ответ от календаря 2 по дате выезда """

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        date = data['check_in']
        command = data['command']

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                call.message.chat.id,
                                call.message.message_id,
                         reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата выезда{emoji.emojize('🔙')}: {result}",
                                call.message.chat.id,
                                call.message.message_id)
        date_format = "%d-%m-%Y"
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = date.strftime(date_format)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_out'] = result.strftime(date_format)

        check_in = datetime.datetime.strptime(data['check_in'], date_format)
        check_out = datetime.datetime.strptime(data['check_out'], date_format)
        days_in_hotel = (check_out - check_in).days

        bot.set_state(call.from_user.id, days_in_hotel, call.message.chat.id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['days_in_hotel'] = days_in_hotel

        if command == 'custom':

            bot.send_message(call.from_user.id, f"\nГород: {data['city'].title()}\n"
                                                f"Количество отелей  : {data['hotel_qty']}\n"
                                                f"Количество фотографий: {data['photo']}\n"
                                                f"Дата заселения: {data['check_in']}\n"
                                                f"Дата выезда: {data['check_out']}\n"
                                                f"Всего дней проживания: {data['days_in_hotel']}\n"
                                                f"Стоимость за ночь = от {data['min_price']} до {data['max_price']} $\n"
                                                f"\nПроверьте Ваши данные, если все в порядке, нажмите - Да", reply_markup=keyboards_answr.yes_no())

        else:
            bot.send_message(call.from_user.id, f"\nГород: {data['city'].title()}\n"
                                                f"Количество отелей : {data['hotel_qty']}\n"
                                                f"Количество фотографий: {data['photo']}\n"
                                                f"Дата заселения: {data['check_in']}\n"
                                                f"Дата выезда: {data['check_out']}\n"
                                                f"Всего дней проживания: {data['days_in_hotel']}\n"
                                                f"\nПроверьте Ваши данные, если все в порядке, нажмите - Да", reply_markup=keyboards_answr.yes_no())

        bot.set_state(call.from_user.id, States.final, call.message.chat.id)


@bot.callback_query_handler(func=None, state=States.final)
@decor_time.chek_time
def get_hotels(call):
    """Отправка запроса к API по ID города.
    Парсинг ответа, получение ID отелей и других данных.
     При необходимости снова запрос для получения фото и адреса.
     Запись данных о пользователе и отелях в БД"""

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        command = data['command']
        data['date_time'] = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        data['chat_id'] = call.message.chat.id

    if call.data == "да":
        bot.send_message(call.from_user.id, text=f"Поиск вариантов по Вашему запросу, подождите несколько секунд... {emoji.emojize('🧐')}")
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            cust_data = data
            # print(cust_data)
        hotels_list = get_hotel_list(cust_data=cust_data)
        # print(hotels_list)
        hotels_qty = int(data['hotel_qty'])
        hotel_days = int(data['days_in_hotel'])
        city_name = data['city']
        time_now = data['date_time']
        count = 0
        try:
            for hotel in range(hotels_qty):
                hotel_id = int(hotels_list['data']['propertySearch']['properties'][hotel]['id'])
                hotel_name = hotels_list['data']['propertySearch']['properties'][hotel]['name']

                hotel_price = round(float(hotels_list['data']['propertySearch']['properties'][hotel]['price']['lead']['amount']), 2)

                common_price = round(float(hotel_price * hotel_days), 2)

                hotel_location = hotels_list['data']['propertySearch']['properties'][hotel]['destinationInfo']['distanceFromDestination']['value']

                hotel_details = get_hotel_details(hotel_id=hotel_id)
                hotel_address = hotel_details['data']['propertyInfo']['summary']['location']['address']['addressLine']
                hotel_data = {
                    'chat_id': call.message.chat.id,
                    'city_name': city_name,
                    'hotel_id': hotel_id,
                    'hotel_name': hotel_name,
                    'hotel_price': hotel_price,
                    'common_price': common_price,
                    'hotel_address': hotel_address,
                    'hotel_days': hotel_days,
                    'hotel_location': hotel_location,
                    'date_time': time_now
                }
                if command == 'custom':
                    if data['min_price'] < hotel_price < data['max_price']:
                        bot.send_message(call.from_user.id, text=f"Данные по отелю {hotel_name}: "
                                                              f"\nАдрес: {hotel_address}"
                                                              f"\nРасстояние от центра города = {hotel_location} км"
                                                              f"\nСтоимость за 1 ночь = {hotel_price} $"
                                                              f"\nОбщая стоимость за {hotel_days} дней = {common_price} $")
                        if data['photo']:
                            bot.send_message(call.from_user.id, text='Фотографии отеля:')
                            hotel_photos = data['photo']
                            for photo in range(hotel_photos):
                                photo_url = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['url']
                                description = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['description']
                                bot.send_message(call.from_user.id, text=f"{description}\n{photo_url}")
                                add_response_to_db(hotel_data=hotel_data)
                                count += 1
                    else:
                        break

                else:
                    add_response_to_db(hotel_data=hotel_data)
                    count += 1
                    bot.send_message(call.from_user.id, text=f"Данные по отелю {hotel_name}: "
                                                          f"\nАдрес: {hotel_address}"
                                                          f"\nРасстояние от центра города = {hotel_location} км"
                                                          f"\nСтоимость за 1 ночь = {hotel_price} $"
                                                          f"\nОбщая стоимость за {hotel_days} дней = {common_price} $")
                    if data['photo']:
                        bot.send_message(call.from_user.id, text='Фотографии отеля:')
                        hotel_photos = data['photo']
                        for photo in range(hotel_photos):
                            photo_url = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['url']
                            description = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['description']
                            bot.send_message(call.from_user.id, text=f"{description}\n{photo_url}")

            if command == 'custom' or 'lowprice':
                if count == 0:
                    bot.send_message(call.from_user.id, text='К сожалению, отеля с вашими требованиями не найдено.'
                                                          'Попробуйте изменить запрос\n\nВернуться назад /help')
                else:
                    bot.send_message(call.from_user.id, text='Это все найденные варианты, которые подходят под ваши требования.'
                                                             '\n\nВернуться назад /help')
        except Exception as exc:
            bot.send_message(call.from_user.id, text='Ошибка запроса к сайту отелей. Повторите запрос /help.')
            bot.delete_state(call.from_user.id, call.message.chat.id)
            raise Exception(exc)

    else:
        bot.send_message(call.from_user.id,
                         text='Вас не устроил результат? Вернитесь в главное меню /help.')
        bot.delete_state(call.from_user.id, call.message.chat.id)