from config_data import config
import requests


def api_request(method, url, params, headers):
    """Функция для запроса к API
    :param method: метод get или post
    :param url: запрос к API
    :param  params: параметры запроса
    :param headers: заголовки запроса
    :return: функцию запроса к API - GET / POST
    """
    if method == 'POST':
        response_post = requests.post(url=url, headers=headers, json=params)
        return response_post

    elif method == 'GET':
        response_get = requests.get(url=url, headers=headers, params=params)
        return response_get.json()


def city_request(city: str, func=api_request) -> dict:
    """Получение данных от пользователя, с названием городов."""
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    params = {
        "q": city,
        "locale": "en_US",
        "langid": "2016",
        "siteid": "300000001"
    }

    headers = {
        'X-RapidAPI-Key': config.RAPID_API_KEY,
        'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
    }

    """Получение данных об городах с названием, которое указал пользователь"""
    city_data = func('GET', url, params, headers)
    cities = dict()
    for city in city_data['sr']:
        if city['type'] == "CITY":
            city_id = city['gaiaId']
            city_name = city['regionNames']['fullName']
            cities[city_name] = city_id

    return cities


def get_hotel_list(cust_data: dict, func=api_request) -> dict:
    """Запрос на список отелей в выбранном городе"""

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    sort = "PRICE_LOW_TO_HIGH"

    params = {

        "destination": {
            "regionId": f"{cust_data['city_id']}"
        },
        "checkInDate": {
            "day": int(cust_data['check_in'][:2]),
            "month": int(cust_data['check_in'][3:5]),
            "year": int(cust_data['check_in'][-4:])
        },
        "checkOutDate": {
            "day": int(cust_data['check_out'][:2]),
            "month": int(cust_data['check_out'][3:5]),
            "year": int(cust_data['check_out'][-4:])
        },
        "rooms": [
            {
                "adults": 1
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": int(cust_data['hotel_qty']),
        "sort": sort,
        "filters": {
            "availableFilter": "SHOW_AVAILABLE_ONLY"
        }
    }
    if cust_data['command'] == 'custom':
        sort = "DISTANCE"
        """params для запроса custom. добавлена сортировка цен в запрос"""
        params = {
            "destination": {
                "regionId": f"{cust_data['city_id']}"
            },
            "checkInDate": {
                "day": int(cust_data['check_in'][:2]),
                "month": int(cust_data['check_in'][3:5]),
                "year": int(cust_data['check_in'][-4:])
            },
            "checkOutDate": {
                "day": int(cust_data['check_out'][:2]),
                "month": int(cust_data['check_out'][3:5]),
                "year": int(cust_data['check_out'][-4:])
            },
            "rooms": [
                {
                    "adults": 1
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": int(cust_data['hotel_qty']),
            "sort": sort,
            "filters": {
                "price": {
                    "max": cust_data['max_price'],
                    "min": cust_data['min_price']
                },
                "availableFilter": "SHOW_AVAILABLE_ONLY"
            }
        }

    hotel_list = func(
        'POST',
        url,
        params,
        headers,
    )

    return hotel_list.json()


def get_hotel_details(hotel_id, func=api_request):
    """Запрос на подробную информацию об отеле для вывода подробного адреса и фото"""
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    params = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": f"{hotel_id}"
    }

    hotel_details = func('POST', url, params, headers)

    return hotel_details.json()
