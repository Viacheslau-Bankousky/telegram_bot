# Hotels_Searcher_bot

![my_bot](https://www.botmake.ru/assets/img/demo/USSCBOT.jpg)

### This telegram bot is designed for easy search of hotels via the API hotels.com
***
### The main packages and files in the bot structure and their brief description:

#### 1. classes 
* `calendar.py` - contains a custom calendar for entering check-in and check-out dates
from the hotel
* `data_class.py` - contains a class of user data with methods for adding an object 
of the user class to the dictionary (static attribute) with existing objects of this class,
extracting it from there and returning the set attributes to the default values
* `database.py` - contains database table models

#### 2. config_data
* `config.py` - the code from this file finds and loads the virtual environment with 
its variables (if it is not found, a message is displayed on the console). Bot and API tokens
are loaded from the virtual environment. The basic commands of the bot are created

#### 3. database
* `database_methods.py` - contains methods for create/drop database tables, adding information
to the database and extracting it from it
* `hotels.db` -  database file (in project used sqlite database)

#### 4. handlers
* `default_handlers`- contains file `handlers.py` with basic handlers of the main bot commands,
messages, callback functions, calendar
* `handlers_before_request` - contains file `handlers.py` intermediate handlers, from the moment 
the command is entered until API requests are sent
* `handlers_for_request_and_after` - contains file `rapidapi.py`functions for API requests,
processing and displaying the results obtained

#### 5. keyboards
* `inline` - contains inline keyboards
* `reply` - contains reply keyboards

#### 6. logger
* `logger.py` - contains a logger decorator, which displays the data taken as an argument 
to the function and the values returned to it

#### 7. utils
* `set_bot_commands.py` - sets the basic bot commands when it starts 
* `misk`
  * `answers`
    * `answers_for_states` - contains functions for the correct response of the bot
    to the entered messages, depending on its current state
    * `callbacks` - contains custom callback functions (called when one of the inline buttons is pressed)
    
#### 8. `loader.py` - contains a bot instance
#### 9. `main.py` - the main file from which the bot is launched
#### 10. `requirements.txt` - list of external project dependencies

***
### The bot has the following states (type bool):
* `zero_condition` - the state from the moment the bot is turned on until the display of the keyboard with 
the cities found
* `first_condition`- the state from the moment the keyboard with the found cities is displayed until the
`differance_between_commands` function from `handlers.handlers_before_request.handlers` (line 65) is called
* `second_condition` - the state from the moment the `differance_between_commands` function 
from `handlers.handlers_before_request.handlers` (line 65) is called until the `check_out` function from 
`handlers.handlers_before_request.handlers` (line 364) is called
* `third_condition` - the state from the moment the `check_out` function from 
`handlers.handlers_before_request.handlers` (line 364) is called until the `result_waiting` function 
(second function call) from `handlers.handlers_before_request.handlers` (line 564) is called and return True of it
* `fourth_condition` - the state from the moment the `result_waiting` function from 
`handlers.handlers_before_request.handlers` (line 564) is called (second function call) and return True of it
until the moment the keyboard  with a question about viewing photos of hotels is displayed 
(`yes_no_keyboard` from `keyboards.inline.inline_keyboards` - line 56)
* `fifth_condition` - the state from the first display of the required number of hotels until the end of the 
script execution
***

>In each inline keyboard and emoji, its message_id is written to the attribute of the UserData class -
>`id_message_for_delete`and the `delete_message` attribute gets the value True. This is necessary for their subsequent removal using 
> `delete_previous_message` function from `handlers.handlers_before_request.handlers` (line 516)
***

### The sequence of calling functions after starting the bot:
1. The `set_default_command` function from the `utils.set_bot_commands` (line 7) sets the basic commands of the bot
2. The `create_database` function from `database.database_methods` (line 10) creates database 
tables and updates them when the bot is restarted 
3. After entering the `/start` command  by the user, the `send_basic_greeting` function  
from `handlers.default_handlers.handler` (line 16) is called, which  adds the user to the log file, 
displays the greeting and `menu_button` (from `keyboards.reply.menu_button`, line 7)
4. After clicking on the menu button, the `send_answer` function from `handlers.default_handlers.handlers` (line 159) 
is called, which calls the `send_greeting` function from `utils.misk.answers.answers_for_states.answers` (line 12),
which in turn calls the `commands_keyboard` function from `keyboards.inline.inline_keyboards` (line 11), after that 
a list of available commands is displayed on the screen. The `delete_previous_message` function is called 
from `handlers.handlers_before_requesr.handlers` (line 516), which deletes the previous inline keyboard 
if there is one

>If one of the buttons with available commands is pressed: `second_query_handler` function from 
> `handlers.default_handlers.handlers` (line 219) is called, which will catch the entered message
> and will call the callback data processing function from `utils.misk.answers.callbacks.callbacks`
> (If the `/lowprice` command is entered - `low_price` function (line 27); If the `/highprice` command is entered -
> `high_price` function (line 42); If the `/bestdeal` command is entered - `best_deal` function (line 12))

5. Depending on the command entered, the corresponding function is called from `handlers.default_handlers.handlers`:
   * `/lowprice` - `command_low_price` function from `handlers.default_handlers.handlers` (line 74) 
   * `/highprice` - `command_high_price` function from `handlers.default_handlers.handlers` (line 96) 
   * `/bestdeal` - `command_best_deal` function from `handlers.default_handlers.handlers` (line 118) 
   * `/history` - `command_history` function from `handlers.default_handlers.handlers` (line 141) .
***

The functions `command_low_price`, `command_high_price`, `command_best_deal` initialize a variable with
an object of the UserData class by calling the `get_user` method from `classes.data_class` (line 144), 
passing the user's `chat_id` as a parameter. If a user with such `chat_id` if it already exists,
then it is extracted from the dictionary `all_users` (a static attribute of the UserData class),
if not, then an object of the class is created, added to the dictionary.
>Next, this feature (`get_user`) will be used in most functions
***
The functions `command_low_price`, `command_high_price`, `command_best_deal` call `delete_previous_message` 
function from `handlers.handlers_before_requesr.handlers`  (line 516), to delete the previous inline keyboard,
if there is one (this is necessary in case of manual commands entry at any stage of script execution)
***
The functions `command_low_price`, `command_high_price`, `command_best_deal` call the `clear_all`  method 
of the UserData class from `classes.data_class` (line 158), which sets the values of all dynamic attributes 
of the class by default
***
In the functions `command_low_price`, `command_high_price`, `command_best_deal`, the value of the attribute 
of the UserData class `current_command` containing the name of the entered command is set,
then the bot displays the name of the entered command 
***
6. `initial_function`from `handlers.handlers_before_requesr.handlers`  (line 16) adds user to the database
(if he is not there) with `add_user_to_database` function from `database.database_methods` (line 21),
offers to select the city where the hotel will be searched, а  writes the name of next 
function in `next_function` field of the user data class
7. Using `register_next_step_handler` calls the following `check_message` function from 
`handlers.handlers_before_requesr.handlers`  (line 399) which checks whether the entered message is one
of the commands known to the bot or the menu button is pressed. If the message is a command, then the corresponding 
function is called and the script returns to the beginning. If the message is not a command or the menu button is not
pressed, the following function is called, the name of which is taken from the `next_function` field of the user
data class.
>Next, this features (`next_function` and `check_message`) will be used in most functions
8. After entering the city, where the hotel will be searched, the `determination_city` function  from
`handlers.handlers_before_requesr.handlers`  (line 39) is called. A check is performed at the previous stage
of the message, if it is a text (including containing a space character), the name of the city is written 
to the  attribute `city` of the UserData class, the `result_waiting` function  from 
`handlers.handlers_before_requesr.handlers` (line 564) is called. If the message at the previous stage
is not a text or a bot command, a warning message is displayed and the `determination_city` function is called again. 
If the entered message is a command of bot, then through the `check_message` function, the script returns to the start 
of execution.
9. When `result_waiting` function  from `handlers.handlers_before_requesr.handlers` (line 564) is called, 
the following sequence of function calls are performed: `request_to_api` from 
`handlers.handlers_for_request_and_after.rapidapi`(line 165) using the `create_request` function from 
`handlers.handlers for_request_and_after.rapidapi` (line 116) executes an API request. In turn, create_request
gets headers, query strings, URL (to execute the request)  from the `function_selection` function from 
`handlers.handlers_for_request_and_after.rapidapi`(line 94), which calls the `locations` function 
from `handlers.handlers_for_request_and_after.rapidapi` (line 20) which directly returns headers, query strings, URL.
If the attempt to make a request was unsuccessful, a repeat request will be made within three times, the user will
be informed by the appropriate message. After executing the API request, the response is parsed according to the specified parameter and the json file 
is deserialized to obtain a nested dictionary. If there is nothing in the dictionary by the key `entities`,
then a message is displayed that the entered city has not been found and the `determination_city` function from 
`handlers.handlers_before_request.handlers` (line 39) will be called again. 
10. If the dictionary for the specified key (`entities`) is not empty, the `processing_cities` function from
`handlers.handlers_for_request_and_after.rapidapi` (line 212) is called. This function creates a dictionary list
that contains the names of cities as a key and their destination_id as a value. Assigns this list to the attribute 
of the UserData class - `current_buffer` and using the inline keyboard `cities_keyboard` from 
`keyboards.inline.inline_keyboards` (line 107) displays them on the screen.
11. After selecting one of the found cities (pressing the corresponding inline keyboard button), 
the `second_query_handler` function is from `handlers.handlers_before_requesr.handlers` (line 219) is called, 
which calls the `show_hotels` function from `utils.misk.answers.callbacks.callbacks` (line 186), 
which in turn finds the desired hotel in the list that is assigned the attribute of the `UserData` class
(`current_buffer` and writes the `destination_id` (call.data) to the attribute of the same name of the user class 
and calls the following function
12. The `differance_between_commands` function  from `handlers.handlers_before_request.handlers` (line 65) is called.
    * **By selecting `/bestdeal` command:**
      * `minimum_price` function from `handlers.handlers_before_request.handlers` (line 97) is called, which
      offers to choose the minimum cost per day of stay in hotel
      * `maximum_price` from `handlers.handlers_before_request.handlers` (line 134) is called, which
        offers to choose the maximum cost per day of stay in hotel
      * `minimum_distance` from `handlers.handlers_before_request.handlers` (line 172) is called, which
        offers to choose the minimum distance of hotel from city center
      * `maximum_distance` from `handlers.handlers_before_request.handlers` (line 212) is called, which
        offers to choose the maximum distance of hotel from city center
    * **The next stage of the script execution, when entering the command `/bestdeal` and by selecting**
    **`/lowprice` and `/highprice` commands (initially):**
      * `hotels_count` function from `handlers.handlers_before_request.handlers` (line 251)  is called, which 
        offers to select the number of hotels to display on the screen
13. `adults_count` function from `handlers.handlers_before_request.handlers` (line 294) is called, which
offers to choose the number of adults who will stay at the hotel.
14. `date_selection` function from `keyboards.inline.inline_keyboards` (line 86) is called, which
creates a calendar for entering the check-in date to the hotel
15. Processing of the date entered using the calendar is carried out using `first_query_handler`
from `handlers.handlers_before_request.handlers` (line 185). The transition between the calendar 
selection of the arrival date and the departure date is carried out using the attribute 
of the UserData  class - `date_flag` (initially - False)
16. `check_in` function from `handlers.handlers_before_request.handlers` (line 332) - is called, which
checks the entered check-in date at the hotel for correctness (`date_flag` - True)
17. `date_selection` function from `keyboards.inline.inline_keyboards` (line 86) is called, which
creates a calendar for entering the check-out date from the hotel
18. `first_query_handler`from `handlers.handlers_before_request.handlers` (line 185) - performs its current
work (see above)
19. `check_out` function from `handlers.handlers_before_request.handlers` (line 364) - is called, which
checks the entered check-out date from the hotel for correctness 
>If the data is entered in an incorrect format, the corresponding message is displayed on the screen 
>and the current function is called again. If the data is entered correctly, then an entry is made 
> to the corresponding attribute of the UserData class (if necessary)
20. When `result_waiting` function  from `handlers.handlers_before_requesr.handlers` (line 564) is called again, 
the following sequence of function calls are performed: `request_to_api` from 
`handlers.handlers_for_request_and_after.rapidapi`(line 165) using the `create_request` function from 
`handlers.handlers for_request_and_after.rapidapi` (line 116) executes an API request. In turn, create_request
gets headers, query strings, URL (to execute the request)  from the `function_selection` function from 
`handlers.handlers_for_request_and_after.rapidapi`(line 94), which calls the `properties` function 
from `handlers.handlers_for_request_and_after.rapidapi` (line 45) which directly returns headers, query strings, URL.
If the attempt to make a request was unsuccessful, a repeat request will be made within three times, the user will
be informed by the appropriate message. After executing the API request, the response is parsed according to the 
specified parameter and the json file is deserialized to obtain a nested dictionary, which will be  written 
to the attribute of the UserData class - `current_buffer`.
21. `selected_command` function from `handlers.handlers_for_request_and_after.rapidapi` (line 474) is called, which
depending on the initially entered command, it calls the corresponding function:
    * `/lowprice` command - `low_price` function from `handlers.handlers_for_request_and_after.rapidapi` (line 492)
    is called
    * `/highprice` command - `high_price` function from `handlers.handlers_for_request_and_after.rapidapi` (line 517)
    is called
    * `/bestdeal` command - `best_deal` function from `handlers.handlers_for_request_and_after.rapidapi` (line 543)
    is called
    > These functions sort the list of hotels in the specified order and write it to the attribute 
of the user data class(current_buffer).
Initially, there is a division of all available hotels into cost - containing and without it,
using the function `comparison_of_hotels` from `handlers.handlers_for_request_and_after.rapidapi` (line 590) 
22. If `result_waiting` from `handlers.handlers_before_requesr.handlers` (line 564) returned True second time
(third_condition of bot)  - `yes_no_keyboard` from `keyboards.inline.inline_keyboards` (line 56) is called
which offer to user to view photos of hotels.
****
### If the user has decided not to view the photo:
****
The function `second_query_handler` from `handlers.default_handlers.handlers` (line 219) is called (catches 
callback function data).
Then `no_answer` function from `utils.misk.answers.callbacks.callbacks` (line 94) is called (processes callback 
function data).
Then `no_answer_about_photo` function from `handlers.handlers_before_requesr.handlers` (line 463) is called (displays 
a message that there will be no photo viewing).
Then `delete_previous_message` function from `handlers.handlers_before_requesr.handlers` (line 516) is called 
(deletes the previous inline keyboard or emoji).
Then `result_displaying` function from `handlers.handlers_for_request_and_after.rapidapi` (line 234), which
will display the required number of hotels.
****
Before the hotel description is displayed, the following functions are called: 
* `check_photo_answer` function from `handlers.handlers_for_request_and_after.rapidapi` (line 265), which 
will call the next function (see below)
* `price_checker` function from `handlers.handlers_for_request_and_after.rapidapi` (line 294), which
checks if the hotel has a cost and set value of attribute of the user data class (`without_price`) to True or False.
Next text message will be created, using calling `create_text_message` function from 
`handlers.handlers_for_request_and_after.rapidapi` (line 314), which returns the text of the hotel description
after several checks:
  * `find_rating` from `handlers.handlers_for_request_and_after.rapidapi` (line 360) - returns the rating of each hotel
  from the list of hotels passed as an argument. If there is no data, a question mark is returned
  * `find_distance` from `handlers.handlers_for_request_and_after.rapidapi` (line 385) - returns the distance from 
  the city center for each hotel from the list of hotels passed as an argument. If there is no data, a question 
  mark is returned
  * `find_price` from `handlers.handlers_for_request_and_after.rapidapi` (line 400) - returns the cost of accommodation
  per night for each hotel from the list of hotels passed as an argument. If there is no data, a question mark 
  is returned
  * `price_existing` from `handlers.handlers_for_request_and_after.rapidapi` (line 428) - returns the cost
  of accommodation for the entire period of stay for each hotel from the list of hotels passed as an argument. 
  If there is no data, a question mark is returned 
  
> After creating the text of the description of the hotel before returning of if, the data is added to the database 
> using the function `add_results_to_database` from `database.database_methods` (line 37)
  
****
### If the user decided to view photos of hotels:
****
The function `second_query_handler` from `handlers.default_handlers.handlers` (line 219) is called (catches 
callback function data).
Then `yes_answer` function from `utils.misk.answers.callbacks.callbacks` (line 94) is called (processes 
callback function data).
Then `yes_answer_about_photo` function from `handlers.handlers_before_requesr.handlers` (line 441) is called, which asks 
the user for the number of hotel photos, deletes the previous inline keyboard or emoji with `delete_previous_message` function
from `handlers.handlers_before_requesr.handlers` (line 516) and after passing the function of checking the input of basic 
commands (`check_message` from `handlers.handlers_before_requesr.handlers` (line 339) it calls `photo_count` function
from `handlers.handlers_before_requesr.handlers` (line 480), which checks the correctness of the data input,
and if the correct number of photos (up to 10) is entered, the function `result_displaying` 
from `handlers.handlers_for_request_and_after.rapidapi` (line 234) is called, which will display the required number
of hotels.
****
Before the hotel description is displayed: 
* `check_photo_answer` function from `handlers.handlers_for_request_and_after.rapidapi` (line 265) is called, which 
will call the next function (see below)
* `price_checker` function (see above) from `handlers.handlers_for_request_and_after.rapidapi` (line 294), which
checks if the hotel has a cost and set value of attribute of the user data class (`without_price`) to True or False.
* `result_waiting` function from `handlers.handlers_before_requesr.handlers` (line 564) is called,
from which, following sequence of function calls are performed: `request_to_api` from 
`handlers.handlers_for_request_and_after.rapidapi`(line 165) using the `create_request` function from 
`handlers.handlers for_request_and_after.rapidapi` (line 116) executes an API request. In turn, create_request
gets headers, query strings, URL (to execute the request)  from the `function_selection` function from 
`handlers.handlers_for_request_and_after.rapidapi`(line 94), which calls the `photo_viewing` function 
from `handlers.handlers_for_request_and_after.rapidapi` (line 72) which directly returns headers, query strings, URL.
If the attempt to make a request was unsuccessful, a repeat request will be made within three times, the user will
be informed by the appropriate message. After receiving a response from the API, it returns to the `request_to_api` 
function, where the JSON file is parsed and the list of hotel photos is written to the UserData class attribute 
(`photo_buffer`), for subsequent use, after that the True value is returned and the `result_waiting` function is returned 
where `photo_selection` function from `handlers.handlers_for_request_and_after.rapidapi` (line 612) is called, which
retrieves the urls of all photos for each hotel from `photo_buffer`, replaces the string with the substitution 
of the corresponding photo size and adds it to the dictionary of all hotel photos (attribute of the UserData class).
* `create_final_photo_list` function from `handlers.handlers_for_request_and_after.rapidapi` (line 644) is called, which
retrieves the required number of non-repeating urls from the dictionary with all the photos for each hotel (using 
`check_urls` function from `handlers.handlers_for_request_and_after.rapidapi` - line 673). If there are not so many
urls, that the user needs, all available ones are added
* `create_media_group` function from `handlers.handlers_for_request_and_after.rapidapi` (line 694) is called, which
displays a message with a media group (hotel photos and its description)

>The text part of the messages is displayed in the same way as when choosing the option to view hotels without photos
(see above).
****
> When the number of hotels specified by the user is displayed, the function `show_more_hotels_part_1` from
`keyboards.inline.inline_keyboards` (line 153) is called, which  will offer to find more hotels according
to the specified parameters, start a new search or end the search. If initially fewer hotels were found than 
the user entered, then the function `show_more_hotels_part_2` from `keyboards.inline.inline_keyboards` (line 192) 
is called, which  suggests starting a new search or ending it. A button with the hotel website is attached to the
message with the description of the hotel (`visit_the_website` function from `keyboards.inline.inline_keyboards`- line 135)  

>If, after displaying the specified number of hotels, the user wants to see more with the same parameters, 
> the function `second_query_handler` from `handlers.default_handlers.handlers` (line 219)  is called, which catches
> callback function data and calls `new_hotels` function from `utils.misk.answers.callbacks.callbacks` (line 116),
> which processes callback function data and cals `delete_previous_message` function from 
> `handlers.handlers_before_request.handlers` (line 516) and `delete_showed_hotels` function from
> `handlers.handlers_for_request_and_after.rapidapi`(line 453), which removes the display of hotels 
> and the list of hotels stored in the attribute of the UserData class (`current_buffer`).
> Next, `result_displaying` function from `handlers.handlers_for_request_and_after.rapidapi` (line 234) is called again
 
> If the user chooses to start a new search the function `second_query_handler` 
> from `handlers.default_handlers.handlers` (line 219)  is called, which catches callback function data and calls
> `new_search` function from `utils.misk.answers.callbacks.callbacks` (line 138), which processes callback function data
> and cals `commands_keyboard` from `keyboard.inline.inline_keyboards` (line 11), which shows list of all available commands

>If the user chooses to end the search for hotels the function `second_query_handler` 
> from `handlers.default_handlers.handlers` (line 219)  is called, which catches callback function data and calls
> `end_search` function from `utils.misk.answers.callbacks.callbacks` (line 138), which processes callback function data
> and cals `delete_previous_message` function from `handlers.handlers_before_request.handlers` (line 516).
> The `clear_all` method is called on an object of the UserData class sets all its attributes to the default position
> After that, you can click on the menu button again and use the bot.
****

### If the /history command is entered by inline keyboard:
* The function `second_query_handler` from `handlers.default_handlers.handlers` (line 219) is called (catches 
callback function data)
* Then `history` function from `utils.misk.answers.callbacks.callbacks` (line 57) is called (processes 
callback function data)
* `command_history` function from `handlers.default_handlers.handlers` (line 141) is called, which delete
the previous inline keyboard or emoji using `delete_previous_message` function  
from `handlers.handlers_before_requesr.handlers` (line 516), and retrieves data from the database
using `pull_from_database` function from database.database_methods (line 54)

>If the `/history` command is entered manually, the function `command_history`
> from `handlers.default_handlers.handlers` (line 141) is called immediately
****

### Depending on the current state (except for the third), the bot reacts to different messages in different ways:
Using `send_answer` function from `handlers.default_handlers.handlers` (line 159) the entered messages are intercepted 
and next functions will be called:
* `zero_condition` - `send_greeting` function from `utils.misk.answers.answers_for_states.answers` (line 12) is called,
which reacts to pressing the menu button and calls the function `commands_keyboard` from 
`keyboards.inline.inline_keyboards` (line 11), responds to the message hello (in Russian and in any case of spelling)
or offers to use the menu button if any other message is entered
* `first_condition` - `send_initial_answer` from `utils.misk.answers.answers_for_states.answers` (line 35) is called,
which reacts to pressing the menu button and calls the function `commands_keyboard` (see above) or offers to use 
the menu button if any other message is entered
* `second_condition` - `send_middle_answer` from `utils.misk.answers.answers_for_states.answers` (line 57) is called,
which reacts to pressing the menu button and calls the function `commands_keyboard` (see above), prompts the user 
to use the inline calendar if there is an attempt to enter the date manually or suggests using the menu button
if any other message is entered
* `fourth_condition` - `send_next_middle_answer` from `utils.misk.answers.answers_for_states.answers` (line 88) is called,
which reacts to pressing the menu button and calls the function `commands_keyboard` (see above), reacts to a manually
entered yes or no answer (in any case of writing), a question about viewing hotel photos or suggests  using the
menu button if any other message is entered
* `fifth_condition` - `send_last_answer` from `utils.misk.answers.answers_for_states.answers` (line 119) is called,
which reacts to pressing the menu button and calls the function `commands_keyboard` (see above) or suggests  using the
menu button if any other message is entered.

>From the first to the fifth state (inclusive), the previous inline keyboards is deleted and displayed again 
> after the bot message (first_condition - `cities_keyboard` from `keyboards.inline.inline_keyboards` (line 107),
> second_condition - `date_selection` from `keyboards.inline.inline_keyboards` (line 86), fourth_condition - 
> `yes_answer_about_photo` from `handlers.handlers_before_request.handlers` (line 441), `no_answer_about_photo`
> from `handlers.handlers_before_request.handlers` (line 463) or `yes_no_keyboard` 
> from `keyboards.inline.inline_keyboards` (line 56), fifth_condition - `show_more_hotels_part_1` 
> from `keyboards.inline.inline_keyboards` (line 153), `show_more_hotels_part_2` 
> from `keyboards.inline.inline_keyboards` (line 192)).
****

### Basic commands of bot:
* `/start` – start and restart the bot;
* `/lowprice` –search for hotels with a minimum cost;
* `/highprice` – search for hotels with the maximum cost;
* `/bestdeal` – search for hotels that are most suitable for 
distance from the city center and cost;
* `/history` – displays the search history.
###### note: 
    you can enter either manually at any time, or by pressing the menu button 
    and then selecting the appropriate command in the inline keyboard.
### Additional commands:
* `/help` – displays a message that you need to use the "menu"
button to get information about all available bot commands (`help_me` function 
from `handlers.default_handlers.handlers` - line 37).
* `/hello-world` – displays a message that the world also welcomes
the user (`say_hello_world` function from `handlers.default_handlers.handlers` - line 56)
###### note:
    you can only enter manually at any time

> Additional commands work using the `check_condition_for_two_commands` function 
> from `handlers.handlers_before_request.handlers` (line 536), which removes the previous inline keyboard and,
> depending on the current state of the bot, outputs it again (first_condition - `cities_keyboard` 
> from `keyboards.inline.inline_keyboards` (line 107), second_condition - `date_selection` 
> from `keyboards.inline.inline_keyboards` (line 86), fourth_condition - `yes_no_keyboard` 
> from `keyboards.inline.inline_keyboards` (line 56), fifth_condition - `show_more_hotels_part_1` 
> from `keyboards.inline.inline_keyboards`  (line 153), if `start_from_the_beginning_part_1` 
> (attribute of the UserData class) is True, `show_more_hotels_part_2` from `keyboards.inline.inline_keyboards` 
> (line 192), if `start_from_the_beginning_part_2` (attribute of the UserData class) is True)

### Getting started
#### To launch the bot, you need:
* Clone the repo (`git clone https://gitlab.skillbox.ru/Bankousky_Viacheslau/python_basic_diploma.git`)
* `cd` into the new directory `python_basic_diploma`
* Create a new virtual environment `venv` in the directory (`python -m virtualenv venv`)
* Activate the new environment (`source venv/bin/activate`)
* Install dependencies in new environment (`pip install -r requirements.txt`);
* Create a file .env in the project directory where you save RAPIDAPI_KEY and token from your bot
(example file in `.env.template`).


