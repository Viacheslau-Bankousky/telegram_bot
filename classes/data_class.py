from datetime import date
from typing import Optional, List, Dict, Union, Set


class UserData:
    """Class for recording temporary data during execution
    script and quick access to it

    :param: user_name: users first name, which has set by him earlier 
    :type: user_name: string
    :param: current_command: the command, that the user entered
    :type: current_command: string
    :param: city:  the city selected by the user
    :type: city:  string
    :param: hotels_count:  the number of hotels entered by the user
    :type: hotels_count: integer
    :param: hotel_id: id of the selected hotel in case of viewing photos
    :type: hotel_id: string
    :param: current_hotel_index: the index of each of the hotels in the list, in the process
    of sequential display by the bot
    :type: current_hotel_index: integer
    :param: destination_id: destination_id  of the selected city
    :type: destination_id: string
    :param: answer_about_foto:  will photos be displayed ?  (yes/no)
    :type: answer_about_foto: string
    :param: photo_count: photos count entered by the user
    :type: foto_count: integer
    :param: adults_count: number of adults checking into the hotel
    :type: adults_count: string
    :param: check_in:  check-in date at the hotel
    :type: check_in:  date object
    :param: check_out:  check-out date from the hotel
    :type: check_out:  date object
    :param: minimum_price: minimum price per night at the hotel
    :type: minimum_price: integer
    :param: maximum_price: maximum price per night at the hotel
    :type: maximum_price: integer
    :param: minimum_distance: minimum hotel distance from the city center (in km)
    :type: minimum_distance: integer
    :param: maximum_distance: maximum hotel distance 
    from the city center (in km)
    :type: maximum_distance: integer
    :param: date_buffer: attribute for temporary recording of check-in dates
    and eviction from the default_handlers and convenient access to them from 
    the corresponding  handler from the handlers_before_request
    :type: date_buffer: date object
    :param: date_flag: the 'switch' attribute, for redirecting dates
    check-ins and check-outs from the default_handlers to the corresponding handler 
    (check_in or check_out) from the handlers_before_request
    :type: date_flag: bool
    :param: zero_condition: the state from the moment the bot is turned on
    until the display of the keyboard with the cities found 
    :type: zero_condition: bool
    :param: first_condition: the state from the moment the keyboard 
    with the found cities is displayed until the differance_between_commands function
    from handlers_before_request is called
    :type: first_condition: bool
    :param: second_condition: the state from the moment the differance_between_commands function 
    from handlers_before_request is called until the check_out function from handlers_before_request 
    is called
    :type: second_condition: bool
    :param: third_condition: the state from the moment the check_out function
    from handlers_before_request is called until the result_waiting function (second function call) from
    handlers_before_request is called and return True of it
    :type: third_condition: bool
    :param: fourth_condition: the state from the moment the result_waiting 
    function from handlers_before_request is called (second function call) and return True of it
    until the moment the keyboard  with a question about viewing photos of hotels is displayed
    :type: fourth_condition: bool
    :param: fifth_condition: the state from the first display of the required number 
    of hotels until the end of the script execution
    :type: fifth_condition: bool
    :param: next_function: the name of the function in the function chain that will be called
    next
    :type: next_function: string
    :param: id_message_for_delete: message id with inline keyboard,
    subject to deletion, in case it has not been used.
    :type: id_message_for_delete: string
    :param: delete_message: the presence of a message that can be deleted
    :type: delete_message: bool
    :param: current_buffer: When call the API for the first time: contains
    a deserialized JSON file with the cities found. Next, this attribute is replaced 
    with a list of dictionaries, where the key is the name of the city, the value is its
    destination_id. When call the API for the second time: contains 
    a deserialized JSON file with hotels found by destination_id. 
    Next, this attribute is replaced with a list of dictionaries, with hotels 
    sorted by price. 
    :type: current_buffer: dictionary of dictionaries or list of dictionaries
    :param : photo_buffer: deserialized JSON file with hotel photos (the third and 
    subsequent API call)
    :type: photo_buffer: dictionary of dictionaries 
    :param: hotels_photos: dictionary with photos of all hotels (after the json file is processed)
    :type: hotels_photos:  dictionary, where the key
    is hotel_id, the value is set with the photo urls
    :param: connect_attempt: number of API call attempts made
    :type: connect_attempt: integer
    :param: start_from_the_beginning_part_1: the first display of the specified 
    number of hotels has been made
    :type: start_from_the_beginning_part_1: bool
    :param: start_from_the_beginning_part_2: no more hotels were found 
    according to the specified parameters
    :type: start_from_the_beginning_part_2: bool
    :param: without_price: indicator on the prevalence of hotels without 
    the cost of living
    :type: without_price: bool
    """""

    all_users: dict = dict()

    def __init__(self):
        self.user_name: str is None
        self.current_command: str is None
        self.city: str is None
        self.hotels_count: int is None
        self.hotel_id: str is None
        self.current_hotel_index: int is None
        self.destination_id: str is None
        self.answer_about_photo: str is None
        self.photo_count: int is None
        self.adults_count: str is None
        self.check_in: date is None
        self.check_out: date is None
        self.minimum_price: int is None
        self.maximum_price: int is None
        self.minimum_distance: int is None
        self.maximum_distance: int is None
        self.date_buffer: date is None
        self.date_flag: bool = False
        self.zero_condition: bool = True
        self.first_condition: bool = False
        self.second_condition: bool = False
        self.third_condition: bool = False
        self.fourth_condition: bool = False
        self.fifth_condition: bool = False
        self.next_function: str is None
        self.id_message_for_delete: str is None
        self.delete_message: bool = False
        self.current_buffer: Optional[Dict, List] is None
        self.photo_buffer: Dict[str: Union[Dict]] is None
        self.hotels_photos: Dict[str: Set] = dict()
        self.connect_attempt: int = 0
        self.start_from_the_beginning_part_1: bool = False
        self.start_from_the_beginning_part_2: bool = False
        self.without_price: bool = False

    @staticmethod
    def get_user(chat_id):
        """Accepts a unique chat ID with the user as a key and returns the user
         object from the dictionary, if such exists, either creates a new one,
         adds it to the dictionary and also returns from there

        :param: chat_id: id of the user's chat
        :type: chat_id: string
        :return: an object of the User data-class
        :rtype: User object"""

        if UserData.all_users.get(chat_id) is None:
            UserData.all_users[chat_id] = UserData()
        return UserData.all_users.get(chat_id)

    def clear_all(self):
        """Updates the values of all dynamic attributes of the user data-class object
    and sets the value to None or bool (the value of user_name remains unchanged, for the subsequent
    correct operation of the bot)"""

        for i_elem in self.__dict__:
            if i_elem == 'date_flag':
                self.__dict__[i_elem] = False
            elif i_elem == 'user_name':
                self.__dict__[i_elem] = self.__dict__[i_elem]
            elif i_elem == 'zero_condition':
                self.__dict__[i_elem] = True
            elif i_elem == 'first_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'second_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'third_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'fourth_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'fifth_condition':
                self.__dict__[i_elem] = False
            elif i_elem == 'delete_message':
                self.__dict__[i_elem] = False
            elif i_elem == 'connect_attempt':
                self.__dict__[i_elem] = 0
            elif i_elem == 'start_from_the_beginning_part_1':
                self.__dict__[i_elem] = False
            elif i_elem == 'start_from_the_beginning_part_2':
                self.__dict__[i_elem] = False
            elif i_elem == 'without_price':
                self.__dict__[i_elem] = False
            elif i_elem == 'hotels_photos':
                self.__dict__[i_elem].clear()
            else:
                self.__dict__[i_elem] = None
