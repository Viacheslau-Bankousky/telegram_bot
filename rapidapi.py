import requests
import json
import emoji
import cmds_keyboard
from re import search, findall
import handlers
from loader import my_bot
from classes import User
from loader import os
from telebot import types
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional, Union, Set, Any
from random import sample
from urllib.request import urlopen

load_dotenv(dotenv_path='.env')


def locations(message: types.Message) -> Tuple[Dict[str, Optional[str]],
                                               Dict[str, str], str]:
    """Contains url, headers and query string for locations/v2/search API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = User.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": os.getenv('API_TOKEN')
    }
    url: str = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring: dict[str: str] = {
        "query": f"{current_user.city}",
        "locale": "ru_RU",
        "currency": "RUB"
    }
    return headers, querystring, url


def properties(message: types.Message) -> Tuple[Dict[str, Optional[str]],
                                                Dict[str, str], str]:
    """Contains url, headers and query string for properties/list API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = User.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": os.getenv('API_TOKEN')
    }
    url: str = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {
        "destinationId": current_user.destination_id, "pageNumber": "1",
        "pageSize": "25", "checkIn": current_user.check_in,
        "checkOut": current_user.check_out,
        "adults1": current_user.adults_count,
        "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"
    }
    return headers, querystring, url


def photo_viewing(message: types.Message) -> Tuple[Dict[str, Optional[str]],
                                                   Dict[str, str], str]:
    """Contains url, headers and query string for properties/get-hotel-photos
    API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = User.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": os.getenv('API_TOKEN')
    }
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": current_user.hotel_id}
    return headers, querystring, url


def function_selection(message: types.Message) -> Tuple[Dict[str, Optional[str]],
                                                        Dict[str, str], str]:
    """Depending on the current state of the bot, it calls the corresponding
    function that returns the url, headers, query string

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = User.get_user(message.chat.id)

    if current_user.zero_condition:
        return locations(message)
    elif current_user.third_condition:
        return properties(message)
    elif current_user.fourth_condition or current_user.fifth_condition:
        return photo_viewing(message)


def create_request(message: types.Message) -> requests.Response:
    """Accepts the url, headers, and query string from ''function_selection''
     and depending on the current state of the bot, it sends the
    request to the API (hotels locations, properties, photo) and returns the response
    object. If an exception occurred, a message is displayed, reconnection is
    performed automatically

    :param message: argument
    :type message: Message object
    :return: response
    :rtype: response object"""

    current_user = User.get_user(message.chat.id)
    headers, querystring, url = function_selection(message)
    try:
        current_user.connect_attempt += 1
        response = requests.get(url, headers=headers,
                                params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Упс, кажется что-то пошло не так.*'
                                     '* Сейчас попробую еще раз*',
                                parse_mode='Markdown')
            if current_user.connect_attempt < 3:
                request_to_api(message)
            else:
                my_bot.send_message(chat_id=message.chat.id,
                                    text='*Сейчас я не могу помочь вам.*'
                                         '* Попробуйте еще раз немного позже*',
                                    parse_mode='Markdown')
                handlers.delete_prev_message(message)
    except requests.exceptions.Timeout:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*Кажется появились какие-то проблемы*'
                                 '* с соединением. Сейчас попробую еще раз*',
                            parse_mode='Markdown')
        if current_user.connect_attempt < 3:
            request_to_api(message)
        else:
            my_bot.send_message(chat_id=message.chat.id,
                                text='*Сервер слишком долго не отвечает*'
                                     '*попробуйте воспользоваться мной немного позже*',
                                parse_mode='Markdown')
            handlers.delete_prev_message(message)


def request_to_api(message: types.Message) -> bool:
    """Gets a response object (from create_request func), performs deserialization
    of json file and writes it down in the corresponding dynamic attribute of the
    User class (current_buffer or photo_buffer). In zero state -  calls the  function
    that creates a list of cities with their destination_id . If the city is not found,
    a message is displayed. In third state - calls a function which sorts hotels
    by price and overwrites them in current_buffer. In all cases, True is returned
    for timely removal of the emoji from handlers.result_waiting/

    :param message: argument
    :type message: Message object
    :return: bool
    """

    current_user = User.get_user(message.chat.id)
    response = create_request(message)
    try:
        if current_user.zero_condition:
            find = search(r'(?<="CITY_GROUP",).+?[\]]', response.text)
            suggestions = json.loads(f'{{{find[0]}}}')
            if len(suggestions["entities"]) != 0:
                current_user.current_buffer = suggestions
                processing_cities(message)
            else:
                my_bot.send_message(chat_id=message.chat.id,
                                    text='*По вашему запросу ничего не найдено.*'
                                         '* Попробуйте выбрать другие варианты*',
                                    parse_mode='Markdown')
        elif current_user.third_condition:
            find = search(r'(?<=,)"results":.+?(?=,"pagination")', response.text)
            suggestions = json.loads(f'{{{find[0]}}}')
            current_user.current_buffer = suggestions
            selected_command(message)
        elif current_user.fourth_condition or current_user.fifth_condition:
            find = search(r'(?<=,)"hotelImages":.+?(?=,"featured)',
                          response.text)
            suggestions = json.loads(f'{{{find[0]}}}')
            current_user.photo_buffer = suggestions
    except (AttributeError, TypeError):
        pass

    return True


def processing_cities(message: types.Message) -> None:
    """Interacts with deserialized json file from the corresponding dynamic
    buffer attribute of the User class, processes it and writes a list with
    the name of cities and destination_id of them, to the same field of the User data
    class. Next, the keyboard with cities is called

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    current_dict = current_user.current_buffer
    current_user.current_buffer = None
    cities = list()
    for i_elem in current_dict["entities"]:
        result = findall(r'[аА-яЯёЁ]+', i_elem["caption"])
        cities.append({' '.join(result): i_elem["destinationId"]})
    current_user.current_buffer = cities
    cmds_keyboard.cities_keyboard(message)


def result_displaying(message: types.Message) -> None:
    """Displays the found hotels with or without photos. If fewer hotels are found
    than the user selected, a message is displayed. After displaying the found
    number of hotels, an inline keyboard is displayed, offering to continue
    the search with the same parameters, start a new search or stop the search.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    if len(hotels) >= current_user.hotels_count:
        for index in range(current_user.hotels_count):
            check_hotels_count(message, hotels=hotels, index=index)
        cmds_keyboard.show_more_hotels_part_1(message)
    else:
        for index in range(len(hotels)):
            check_hotels_count(message, hotels=hotels, index=index)
        my_bot.send_message(chat_id=message.chat.id,
                            text='*К сожалению мне удалось найти немного*'
                                 '* меньше отелей(*',
                            parse_mode='Markdown')
        cmds_keyboard.show_more_hotels_part_2(message)


def check_hotels_count(message: types.Message,
                       hotels: List[Union[Dict]], index: int) -> None:
    """Sets the value of the hotel id and its index in the list of hotels,
    calls the function of checking the availability of the cost of accommodation
     in hotels and, depending on the desire to view photos, either calls the
     corresponding photo display function, or displays hotels without photos

    :param index: index of hotel from list of them
    :type: index: integer
    :param hotels: list of hotels
    :type: hotels: List of dictionaries
    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    current_user.hotel_id = hotels[index]['id']
    current_user.current_hotel_index = index
    price_checker(message, hotels=hotels, index=index)
    if current_user.answer_about_photo == 'ДА':
        handlers.result_waiting(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text=create_text_message(message),
                            reply_markup=cmds_keyboard.visit_the_website(message),
                            parse_mode='Markdown')


def create_text_message(message: types.Message) -> str:
    """Creates and returns a text message with a description of each hotel

    :param message: argument
    :type message: Message object
    :return: description of the hotel
    :rtype: string"""

    current_user = User.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    index: int = current_user.current_hotel_index
    # This design is used to determine the total length of stay at the hotel
    date_diff: List[int] = [
        int(m) for m in str(current_user.check_out - current_user.check_in)
        if m.isdigit()
    ]
    if date_diff[0] == 0:
        date_diff[0] = 1
    return emoji.emojize(':hotel: Название отеля: '
                         f'{hotels[index].get("name", "")}\n'
                         ':magnifying_glass_tilted_right: Адрес: '
                         f'{hotels[index]["address"].get("streetAddress", ":house_with_garden:")}'
                         f'{hotels[index]["address"].get("extendedAddress", ":house_with_garden:")}\n'
                         ':bar_chart: Общий рейтинг отеля: '
                         f'{hotels[index]["starRating"]}\n'
                         f':chart_increasing: Рейтинг посетителей: '
                         f'{find_key(hotels[index], "guestReviews", "rating")}\n'
                         f':microscope: Оценка посетителей: '
                         f'{find_key(hotels[index], "guestReviews", "badgeText")}\n'
                         f':pinching_hand: Расстояние от центра города: '
                         f'{hotels[index]["landmarks"][0]["distance"]}\n'
                         ':coin: Цена за сутки: '
                         f'{find_next_key(hotels[index], "ratePlan", "price", "exactCurrent")} RUB\n'
                         f':money_bag: Цена за {date_diff[0]} дней проживания: '
                         f'{price_do_not_exist(message, date_diff)}'
                         f' RUB\n')


def find_key(some_dict: Dict, first_key: str, second_key: str) -> str:
    """It is used to search for values (the user rating of the hotel and its user rating)
    in the hotel dictionary by the corresponding keys. Emogi is returned
    if the key passed to the function does not exist  or the value is returned by
    the dictionary key, if it exists

    :param: some_dict: current hotel from hotels list
    :type: some_dict: dictionary
    :param: first_key: first key from some_dict
    :type: first_key: string
    :param: second_key: second key of  nested dictionary from some_dict
    :type: second_key: string
    :return: hotel rating or question emoji sign
    :rtype: string"""

    if some_dict.get(first_key):
        if some_dict[first_key].get(second_key):
            return some_dict[first_key][second_key]
        else:
            return ":red_question_mark:"
    else:
        return ":red_question_mark:"


def find_next_key(some_dict: Dict, first_key: str,
                  second_key: str, third_key: str) -> str:
    """It is used to search for values (hotel price) in the hotel dictionary by
    the corresponding keys. Emogi is returned if the key passed to the function
     does not exist  or the value is returned by the dictionary key, if it exists

    :param: some_dict: current hotel from hotels list
    :type: some_dict: dictionary
    :param: first_key: first key from some_dict
    :type: first_key: string
    :param: second_key: second key of  nested dictionary from some_dict
    :type: second_key: string
    :param: third_key: third key of  nested dictionary from some_dict
    :type: second_key: string
    :return: hotel price or question emoji sign
    :rtype: string"""

    if some_dict.get(first_key):
        if some_dict[first_key].get(second_key):
            if some_dict[first_key][second_key].get(third_key):
                return some_dict[first_key][second_key][third_key]
        else:
            return ":red_question_mark:"
    else:
        return ":red_question_mark:"


def price_do_not_exist(message: types.Message,
                       duration: List[int]) -> Union[str, int]:
    """Returns emoji question sign if the hotel has no cost or returns the cost
    for the duration of the stay at the hotel

    :param duration: length of stay at the hotel
    :type: duration: list with one integer
    :param message: argument
    :type message: Message object
    :return: question emoji sign or cost per total stay at the hotel
    :rtype: string or integer"""

    current_user = User.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    index: int = current_user.current_hotel_index

    if current_user.without_price:
        return ":red_question_mark:"
    else:
        return round(
            hotels[index]["ratePlan"]["price"]["exactCurrent"] * duration[0], 2
        )


def delete_showed_hotels(message: types.Message) -> None:
    """Deletes the number of hotels entered by the user from current_buffer,
    after they are displayed. If the list of hotels is empty, a keyboard is displayed
    with a suggestion to start a new search or finish the one you started

    :param message: argument
    :type message: Message object
    :return: None
    """
    current_user = User.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    try:
        for index in range(current_user.hotels_count):
            hotels.remove(hotels[index])
        result_displaying(message)
    except IndexError:
        cmds_keyboard.show_more_hotels_part_2(message)


def price_checker(message: types.Message,
                  hotels: List[Union[Dict]], index: int) -> None:
    """Checks if the hotel has a cost and sets the corresponding flag to True,
     if available

     :param: message: argument
    :type: message: Message object
    :param: hotels: list of hotels
    :type: hotels: list of dictionaries
    :param: index: index of hotel from list of them
    :type: index: integer"""

    current_user = User.get_user(message.chat.id)
    if hotels[index].get("ratePlan"):
        current_user.without_price = False
    else:
        current_user.without_price = True


def selected_command(message: types.Message) -> None:
    """Depending on the command entered by the user, it calls
    the corresponding function

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    if current_user.current_command == '/lowprice':
        low_price(message)
    elif current_user.current_command == '/highprice':
        high_price(message)
    elif current_user.current_command == '/bestdeal':
        best_deal(message)


def low_price(message: types.Message) -> None:
    """Accepts lists of dictionaries of hotels containing their cost and without it.
    If the list of hotels with a price is not empty, it sorts it in ascending order
    of price and adds hotels without a price from another list to the end.
    If initially the list of hotels with a price is empty, then further work is carried
    out only with hotels without a price from the corresponding folder.
    The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    if len(hotels_with_price) > 0:
        sorted(hotels_with_price,
               key=lambda x: x["ratePlan"]["price"]["exactCurrent"])
        hotels_with_price.extend(hotels_without_price)
        current_user.current_buffer = hotels_with_price
    else:
        current_user.current_buffer = hotels_without_price


def high_price(message: types.Message) -> None:
    """Accepts lists of dictionaries of hotels containing their cost and without it.
    If the list of hotels with a price is not empty, it sorts it in descending order
    of price and adds hotels without a price from another list to the end.
    If initially the list of hotels with a price is empty, then further work is carried
    out only with hotels without a price from the corresponding folder.
    The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    if len(hotels_with_price) > 0:
        sorted(hotels_with_price,
               key=lambda x: x["ratePlan"]["price"]["exactCurrent"], reverse=True)
        hotels_with_price.extend(hotels_without_price)
        current_user.current_buffer = hotels_with_price
    else:
        current_user.current_buffer = hotels_without_price


def best_deal(message: types.Message) -> None:
    """Accepts lists of dictionaries of hotels with and without their cost.
    If the list of hotels with a price is not empty, then hotels are added from
    it to another list, taking into account the price range and distance from
    the city center set earlier. Next, sorting carried out by distance from the
    city center. If initially the list of hotels with a price is empty, then further
    work is carried out only with hotels without a price from the corresponding folder.
    The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    final_hotels_list: List = list()
    if len(hotels_with_price) > 0:
        for i_elem in hotels_with_price:
            if current_user.max_price >= i_elem["ratePlan"]["price"]["exactCurrent"] >= (
                    current_user.min_price) and current_user.max_distance >= (
                    int([i_sym for i_sym in i_elem["landmarks"][0][
                        "distance"] if i_sym.isdigit()][0])) >= (
                    current_user.min_distance):
                final_hotels_list.append(i_elem)
        sorted(final_hotels_list, key=lambda x: (x["landmarks"][0]["distance"]))
        final_hotels_list.extend(hotels_without_price)
        current_user.current_buffer = hotels_with_price
    else:
        current_user.current_buffer = hotels_without_price


def comparison_of_hotels(message: types.Message) -> Tuple[list, list]:
    """Adds hotels to one list with the availability of the cost of living, and to another
         without it, and returns both of them

    :param message: argument
    :type message: Message object
    :return: hotels with and without price
    :rtype: tuple of lists"""

    current_user = User.get_user(message.chat.id)
    hotels_list_with: List = list()
    hotels_list_without: List = list()
    for i_hotel in current_user.current_buffer["results"]:
        if not i_hotel.get("ratePlan") is None:
            hotels_list_with.append(i_hotel)
        else:
            hotels_list_without.append(i_hotel)
    return hotels_list_with, hotels_list_without


def photo_selection(message: types.Message) -> None:
    """Retrieves the urls of all photos for each hotel from photo_buffer,
     replaces the string with the substitution of the corresponding photo
     size and adds it to the dictionary of all hotel photos. At the end, a
     function is called that displays a message with a media group.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    photo: Set = set()
    try:
        for i_key, i_value in current_user.photo_buffer.items():
            if i_key == "hotelImages":
                if len(i_value) > 0:
                    for i_elem in i_value:
                        photo.add(i_elem.get("baseUrl").replace('{size}', 'z'))
            elif i_key == "roomImages":
                if len(i_value) > 0:
                    for i_elem in i_value[0]["images"]:
                        photo.add(i_elem.get("baseUrl").replace('{size}', 'z'))

        current_user.hotels_photos[current_user.hotel_id] = photo
        create_final_photo_list(message)
    except IndexError:
        pass


def create_media_group(message: types.Message, photo: List[Union[str]]) -> None:
    """Displays a message with a media group and at the end displays another
     message with an inline button (hotel website)

     :param photo: list with hotel urls
     :type photo: list with strings
     :param message: argument
    :type message: Message object
    :return: None"""

    my_bot.send_media_group(message.chat.id,
                            [types.InputMediaPhoto(urlopen(url),
                                                   caption=create_text_message(message))
                             if photo.index(url) == 0
                             else types.InputMediaPhoto(urlopen(url))
                             for url in photo])
    my_bot.send_message(chat_id=message.chat.id,
                        text=emoji.emojize(
                            '*Для просмотра дополнительных опций и фотографий *'
                            '* посетите  :backhand_index_pointing_down:*'),
                        reply_markup=cmds_keyboard.visit_the_website(message),
                        parse_mode='Markdown')


def create_final_photo_list(message: types.Message) -> None:
    """Retrieves the required number of non-repeating urls from the
    dictionary with all the photos for each hotel. If there are not so many urls
    that the user needs, all available ones are added. Calls the function that
    sends the media group

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = User.get_user(message.chat.id)
    try:
        final_photo: List[Union[str]] = sample(current_user.hotels_photos[
                                                   current_user.hotel_id],
                                               current_user.photo_count)
        create_media_group(message, final_photo)
    except ValueError:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*У следующего отеля будет  меньше фото,*'
                                 '* чем вы хотели*', parse_mode='Markdown')
        final_photo: List[Union[str]] = sample(
            current_user.hotels_photos[current_user.hotel_id], len(
                current_user.hotels_photos[current_user.hotel_id])
        )
        create_media_group(message, final_photo)
