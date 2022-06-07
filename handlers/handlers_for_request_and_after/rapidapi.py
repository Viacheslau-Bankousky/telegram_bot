from loader import my_bot
from config_data import config
from telebot.types import Message, InputMediaPhoto
from typing import Dict, List, Tuple, Optional, Union, Set
from classes.data_class import UserData
import handlers.handlers_before_request.handlers as handlers
from random import sample
import requests
import json
import emoji
from re import search, findall
import keyboards.inline.inline_keyboards as inline
from logger.logger import logger_wraps, logger
import database.database_methods as database


@logger_wraps()
def locations(message: Message) -> Tuple[Dict[str, Optional[str]],
                                         Dict[str, str], str]:
    """Contains url, headers and query string for locations/v2/search API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = UserData.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": config.RAPID_API_KEY
    }
    url: str = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring: dict[str: str] = {
        "query": f"{current_user.city}",
        "locale": "ru_RU",
        "currency": "RUB"
    }
    return headers, querystring, url


@logger_wraps()
def properties(message: Message) -> Tuple[Dict[str, Optional[str]],
                                          Dict[str, str], str]:
    """Contains url, headers and query string for properties/list API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = UserData.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": config.RAPID_API_KEY
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


@logger_wraps()
def photo_viewing(message: Message) -> Tuple[Dict[str, Optional[str]],
                                             Dict[str, str], str]:
    """Contains url, headers and query string for properties/get-hotel-photos
    API Hotels.com

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = UserData.get_user(message.chat.id)
    headers: dict[str: str] = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": config.RAPID_API_KEY
    }
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": current_user.hotel_id}
    return headers, querystring, url


@logger_wraps()
def function_selection(message: Message) -> Tuple[Dict[str, Optional[str]],
                                                  Dict[str, str], str]:
    """Depending on the current state of the bot, it calls the corresponding
    function that returns the url, headers, query string

    :param message: argument
    :type message: Message object
    :return: headers, querystring, url
    :rtype: headers, querystring: dictionary with strings
    as key and value; url: string"""

    current_user = UserData.get_user(message.chat.id)

    if current_user.zero_condition:
        return locations(message)
    elif current_user.third_condition:
        return properties(message)
    elif current_user.fourth_condition or current_user.fifth_condition:
        return photo_viewing(message)


@logger_wraps()
def create_request(message: Message) -> requests.Response:
    """Accepts the url, headers, and query string from ''function_selection''
     and depending on the current state of the bot, it sends the
    request to the API endpoint (hotels locations, properties, photo) and returns the response
    object. If an exception occurred, a message is displayed, reconnection is
    performed automatically, the previous emoji is being deleted

    :param message: argument
    :type message: Message object
    :return: response
    :rtype: response object"""

    current_user = UserData.get_user(message.chat.id)
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
                handlers.delete_previous_message(message)
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
            handlers.delete_previous_message(message)


@logger_wraps()
def request_to_api(message: Message) -> bool:
    """Gets a response object (from create_request function), performs deserialization
    of json file and writes it down in the corresponding dynamic attribute of the
    User data class (current_buffer or photo_buffer, depending on the current state).
    In zero state - calls the  function that creates a list of cities with their
    destination_id . If the city is not found, a message is displayed. In third
    state - calls a function which sorts hotels by price and overwrites them in
    current_buffer. In all cases, True is returned for timely removal of the emoji
     from result_waiting function from handlers_before_request

    :param message: argument
    :type message: Message object
    :return: bool
    """

    current_user = UserData.get_user(message.chat.id)
    response = create_request(message)
    try:
        if current_user.zero_condition:
            find = search(r'(?<="CITY_GROUP",).+?[\]]', response.text)
            suggestions = json.loads(f'{{{find[0]}}}')
            if len(suggestions["entities"]) != 0:
                current_user.current_buffer = suggestions
                processing_cities(message)
            else:
                result = my_bot.send_message(chat_id=message.chat.id,
                                             text='*По вашему запросу ничего не найдено.*'
                                                  '* Попробуйте выбрать другие варианты*',
                                             parse_mode='Markdown')
                my_bot.register_next_step_handler(result, handlers.determination_city)
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
        logger.exception('ups... something went wrong')

    return True


@logger_wraps()
def processing_cities(message: Message) -> None:
    """Interacts with deserialized json file from the corresponding dynamic
    buffer attribute of the User data class, processes it and writes a list with
    the name of cities and destination_id of them, to the same field of the data
    class. Next, the keyboard with cities is called

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    current_dict = current_user.current_buffer
    current_user.current_buffer = None
    cities = list()
    for i_elem in current_dict["entities"]:
        result = findall(r'[аА-яЯёЁ]+', i_elem["caption"])
        cities.append({' '.join(result): i_elem["destinationId"]})
    current_user.current_buffer = cities
    inline.cities_keyboard(message)


@logger_wraps()
def result_displaying(message: Message) -> None:
    """Depending on the current number of hotels, displays the found hotels with
    or without photos (using a special function that takes a list of hotels and
    the index of the current hotel as arguments). If fewer hotels are found than
    the user selected, a message is displayed. After displaying the found number
    of hotels, an inline keyboard is displayed, offering to continue the search
    with the same parameters (if possible), start a new search or stop the search (two
    different inline keyboards, depending on the availability or absence of hotels
    corresponding to the initially set parameters).

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    if len(hotels) >= current_user.hotels_count:
        for index in range(current_user.hotels_count):
            check_photo_answer(message, hotels=hotels, index=index)
        inline.show_more_hotels_part_1(message)
    else:
        for index in range(len(hotels)):
            check_photo_answer(message, hotels=hotels, index=index)
        my_bot.send_message(chat_id=message.chat.id,
                            text='*К сожалению мне удалось найти немного*'
                                 '* меньше отелей(*',
                            parse_mode='Markdown')
        inline.show_more_hotels_part_2(message)


@logger_wraps()
def check_photo_answer(message: Message,
                       hotels: List[Union[Dict]], index: int) -> None:
    """Sets the value of the hotel id and its index in the list of hotels,
    calls the function of checking the availability of the cost of accommodation
    in hotels and, depending on the desire photos viewing, either calls the
    corresponding photo displaying function, or displays hotels without photos

    :param index: index of hotel from list of them
    :type: index: integer
    :param hotels: list of hotels
    :type: hotels: List of dictionaries
    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    current_user.hotel_id = hotels[index]['id']
    current_user.current_hotel_index = index
    price_checker(message, hotels=hotels, index=index)
    if current_user.answer_about_photo == 'ДА':
        handlers.result_waiting(message)
    else:
        my_bot.send_message(chat_id=message.chat.id,
                            text=create_text_message(message),
                            reply_markup=inline.visit_the_website(message),
                            parse_mode='Markdown')


@logger_wraps()
def price_checker(message: Message,
                  hotels: List[Union[Dict]], index: int) -> None:
    """Checks if the hotel has a cost and sets the corresponding flag to True,
     if available

    :param: message: argument
    :type: message: Message object
    :param: hotels: list of hotels
    :type: hotels: list of dictionaries
    :param: index: index of hotel from list of them
    :type: index: integer"""

    current_user = UserData.get_user(message.chat.id)
    if hotels[index].get("ratePlan"):
        current_user.without_price = False
    else:
        current_user.without_price = True


@logger_wraps()
def create_text_message(message: Message) -> str:
    """Creates and returns the text message with a description of each hotel

    :param message: argument
    :type message: Message object
    :return: description of the hotel
    :rtype: string"""

    current_user = UserData.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    index: int = current_user.current_hotel_index
    # This design is used to determine the total length of stay at the hotel
    date_diff: List[int] = [
        int(m) for m in str(current_user.check_out - current_user.check_in)
        if m.isdigit()
    ]
    if date_diff[0] == 0:
        date_diff[0] = 1
    current_message = emoji.emojize(':hotel: Название отеля: '
                         f'{hotels[index].get("name", "")}\n'
                         ':magnifying_glass_tilted_right: Адрес: '
                         f'{hotels[index]["address"].get("streetAddress", ":house_with_garden:")}'
                         f'{hotels[index]["address"].get("extendedAddress", ":house_with_garden:")}\n'
                         ':bar_chart: Общий рейтинг отеля: '
                         f'{hotels[index].get("starRating", ":smiling_face:")}\n'
                         f':chart_increasing: Рейтинг посетителей: '
                         f'{find_rating(hotels[index], "guestReviews", "rating")}\n'
                         f':microscope: Оценка посетителей: '
                         f'{find_rating(hotels[index], "guestReviews", "badgeText")}\n'
                         f':pinching_hand: Расстояние от центра города: '
                         f'{find_distance(hotels[index], "landmarks", "distance")}\n'
                         ':coin: Цена за сутки: '
                         f'{find_price(hotels[index], "ratePlan", "price", "exactCurrent")} RUB\n'
                         f':money_bag: Цена за {date_diff[0]} дней проживания: '
                         f'{price_existing(message, date_diff)}'
                         f' RUB\n')
    database.add_results_to_database(message, result=current_message)
    return current_message


@logger_wraps()
def find_distance(some_dictionary: Dict, first_key: str, second_key: str) -> str:
    """Checks if the hotel has a distance from the city center. Emogi is returned
    if the key passed to the function does not exist  or the value is returned by
    the dictionary key, if it exists"""

    if some_dictionary.get(first_key) and len(some_dictionary[first_key]) > 0:
        if some_dictionary[first_key][0].get(second_key):
            return some_dictionary[first_key][0][second_key]
        else:
            return ":red_question_mark:"
    else:
        return ":red_question_mark:"


@logger_wraps()
def find_rating(some_dictionary: Dict, first_key: str, second_key: str) -> str:
    """It is used to search for values (the user rating of the hotel and its user review)
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

    if some_dictionary.get(first_key):
        if some_dictionary[first_key].get(second_key):
            return some_dictionary[first_key][second_key]
        else:
            return ":red_question_mark:"
    else:
        return ":red_question_mark:"


@logger_wraps()
def find_price(some_dictionary: Dict, first_key: str,
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

    if some_dictionary.get(first_key):
        if some_dictionary[first_key].get(second_key):
            if some_dictionary[first_key][second_key].get(third_key):
                return some_dictionary[first_key][second_key][third_key]
        else:
            return ":red_question_mark:"
    else:
        return ":red_question_mark:"


@logger_wraps()
def price_existing(message: Message,
                   duration: List[int]) -> Union[str, int]:
    """Returns emoji question sign if the hotel has no cost or returns the cost
    for the duration of the stay at the hotel

    :param duration: length of stay at the hotel
    :type: duration: list with one integer
    :param message: argument
    :type message: Message object
    :return: question emoji sign or cost per total stay at the hotel
    :rtype: string or integer"""

    current_user = UserData.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    index: int = current_user.current_hotel_index

    if current_user.without_price:
        return ":red_question_mark:"
    else:
        return round(
            hotels[index]["ratePlan"]["price"]["exactCurrent"] * duration[0], 2
        )


@logger_wraps()
def delete_showed_hotels(message: Message) -> None:
    """Deletes the number of hotels entered by the user from current_buffer,
    after they are displayed. If the list of hotels is empty, a keyboard is displayed
    with a suggestion to start a new search or finish the one you started

    :param message: argument
    :type message: Message object
    :return: None
    """
    current_user = UserData.get_user(message.chat.id)
    hotels: List[Union[Dict]] = current_user.current_buffer
    try:
        for index in range(current_user.hotels_count):
            hotels.remove(hotels[index])
        result_displaying(message)
    except IndexError:
        logger.exception('ups... nothing to delete more')
        inline.show_more_hotels_part_2(message)


@logger_wraps()
def selected_command(message: Message) -> None:
    """Depending on the command entered by the user, it calls
    the corresponding function

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    if current_user.current_command == '/lowprice':
        low_price(message)
    elif current_user.current_command == '/highprice':
        high_price(message)
    elif current_user.current_command == '/bestdeal':
        best_deal(message)


@logger_wraps()
def low_price(message: Message) -> None:
    """Accepts lists of dictionaries of hotels containing their cost and without it.
    If the list of hotels with a price is not empty, it sorts it in ascending
    order of price and adds hotels without a price from another list to the end.
    If initially the list of hotels with a price is empty, then further work is carried
    out only with hotels without a price from the corresponding folder (in the case
    when a city is selected in which there are only hotels without a price, like Gagra).
    The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    if len(hotels_with_price) > 0:
        sorted_list: List = sorted(hotels_with_price,
                                   key=lambda x: x["ratePlan"]["price"]["exactCurrent"])
        sorted_list.extend(hotels_without_price)
        current_user.current_buffer = sorted_list
    else:
        current_user.current_buffer = hotels_without_price


@logger_wraps()
def high_price(message: Message) -> None:
    """Accepts lists of dictionaries of hotels containing their cost and without it.
    If the list of hotels with a price is not empty, it sorts it in descending
    order of price and adds hotels without a price from another list to the end.
    If initially the list of hotels with a price is empty, then further work is carried
    out only with hotels without a price from the corresponding folder (in the case
    when a city is selected in which there are only hotels without a price, like Gagra).
    The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    if len(hotels_with_price) > 0:
        sorted_list: List = sorted(hotels_with_price,
                                   key=lambda x: x["ratePlan"]["price"]["exactCurrent"],
                                   reverse=True)
        sorted_list.extend(hotels_without_price)
        current_user.current_buffer = sorted_list
    else:
        current_user.current_buffer = hotels_without_price


@logger_wraps()
def best_deal(message: Message) -> None:
    """Accepts lists of dictionaries of hotels with and without their cost.
    If the list of hotels with a price is not empty, then hotels are added from
    it to another list, taking into account the price range and distance from
    the city center set earlier. Next, sorting carried out by distance from the
    city center. If initially the list of hotels with a price is empty, then further
    work is carried out only with hotels without a price from the corresponding folder
    (in the case when a city is selected in which there are only hotels without a price,
    like Gagra). The dynamic attribute of the user class is overwritten at the end

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    hotels_with_price, hotels_without_price = comparison_of_hotels(message)
    final_hotels_list: List = list()
    if len(hotels_with_price) > 0:
        for i_element in hotels_with_price:
            current_price = i_element["ratePlan"]["price"]["exactCurrent"]
            initial_remoteness: str = ''.join([i_symbol for i_symbol in i_element[
                "landmarks"][0]["distance"]
                                               if i_symbol.isdigit()
                                               or i_symbol == ','])
            if ',' not in initial_remoteness:
                remoteness = int(initial_remoteness)
            else:
                remoteness = float(initial_remoteness.replace(',', '.'))

            if current_user.maximum_price >= current_price >= (
                    current_user.minimum_price) and (
                    current_user.maximum_distance) >= remoteness >= (
                    current_user.minimum_distance):
                i_element["landmarks"][0]["distance"] = remoteness
                final_hotels_list.append(i_element)
        sorted_list: List = sorted(final_hotels_list, key=lambda x: x[
            "landmarks"][0]["distance"])
        for index in range(len(sorted_list)):
            sorted_list[index]["landmarks"][0]["distance"] = str(
                sorted_list[index]["landmarks"][0]["distance"]) + ' км'
        sorted_list.extend(hotels_without_price)
        current_user.current_buffer = sorted_list
    else:
        current_user.current_buffer = hotels_without_price


@logger_wraps()
def comparison_of_hotels(message: Message) -> Tuple[list, list]:
    """Adds hotels to one list with the availability of the cost of living, and to another
         without it, and returns both of them

    :param message: argument
    :type message: Message object
    :return: hotels with and without price
    :rtype: tuple of lists"""

    current_user = UserData.get_user(message.chat.id)
    hotels_list_with: List = list()
    hotels_list_without: List = list()
    for i_hotel in current_user.current_buffer["results"]:
        if len(i_hotel["landmarks"]) > 0:
            if not i_hotel.get("ratePlan") is None:
                hotels_list_with.append(i_hotel)
            else:
                hotels_list_without.append(i_hotel)
    return hotels_list_with, hotels_list_without


@logger_wraps()
def photo_selection(message: Message) -> None:
    """Retrieves the urls of all photos for each hotel from photo_buffer,
     replaces the string with the substitution of the corresponding photo
     size and adds it to the dictionary of all hotel photos. At the end, a
     function is called that displays a message with a media group.

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    photo: Set = set()
    try:
        for i_key, i_value in current_user.photo_buffer.items():
            if i_key == "hotelImages":
                if len(i_value) > 0:
                    for i_elem in i_value:
                        if i_elem.get("baseUrl"):
                            photo.add(i_elem["baseUrl"].replace('{size}', 'z'))
            elif i_key == "roomImages":
                if len(i_value) > 0:
                    for i_elem in i_value[0]["images"]:
                        if i_elem.get("baseUrl"):
                            photo.add(i_elem["baseUrl"].replace('{size}', 'z'))

        current_user.hotels_photos[current_user.hotel_id] = photo
        create_final_photo_list(message)
    except IndexError:
        logger.exception('something went wrong')


@logger_wraps()
def create_final_photo_list(message: Message) -> None:
    """Retrieves the required number of non-repeating urls from the
    dictionary with all the photos for each hotel. If there are not so many urls
    that the user needs, all available ones are added. Calls the function that
    sends the media group

    :param message: argument
    :type message: Message object
    :return: None"""

    current_user = UserData.get_user(message.chat.id)
    try:
        final_photo: List[Union[str]] = check_urls(message=message,
                                                   photo_count=current_user.photo_count)
        create_media_group(message, final_photo)
    except ValueError:
        my_bot.send_message(chat_id=message.chat.id,
                            text='*У следующего отеля будет  меньше фото,*'
                                 '* чем вы хотели*', parse_mode='Markdown')
        final_photo: List[Union[str]] = check_urls(
            message=message,
            photo_count=len(
                current_user.hotels_photos[
                    current_user.hotel_id])
        )
        create_media_group(message, final_photo)


@logger_wraps()
def check_urls(message: Message, photo_count: int) -> List[Union[str]]:
    """Selects a specified number of active urls from dictionaries with photos
    of each hotel. If at least one url does not work, the selection process is
    repeated

    :param message: argument
    :type message: Message object
    :param photo_count: count of urls
    :type photo_count: integer
    :return: the specified number of hotel urls
    :rtype: list with strings"""

    current_user = UserData.get_user(message.chat.id)
    while True:
        urls_list: List[Union[str]] = sample(current_user.hotels_photos[
                                                 current_user.hotel_id],
                                             photo_count)
        if all([requests.get(url).status_code == 200 for url in urls_list]):
            return urls_list


def create_media_group(message: Message, photo: List[Union[str]]) -> None:
    """Displays a message with a media group (hotel photos and description of it)
     and at the end displays another message with an inline button (hotel website)

    :param photo: list with hotel urls
    :type photo: list with strings
    :param message: argument
    :type message: Message object
    :return: None"""

    my_bot.send_media_group(message.chat.id,
                            [InputMediaPhoto(url,
                                             caption=create_text_message(message))
                             if photo.index(url) == 0
                             else InputMediaPhoto(url)
                             for url in photo])
    my_bot.send_message(chat_id=message.chat.id,
                        text=emoji.emojize(
                            '*Для просмотра дополнительных опций и фотографий *'
                            '* посетите  :backhand_index_pointing_down:*'),
                        reply_markup=inline.visit_the_website(message),
                        parse_mode='Markdown')
