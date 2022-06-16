# Hotels_Searcher_bot
![my_bot](https://mitsoftware.com/wp-content/uploads/2021/02/bot1.png)
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
### The sequence of calling functions after starting the bot:
1. The `set_default_command` function from the `utils.set_bot_commands` (line 7) sets the basic commands of the bot
2. The `create_database` function from `database.database_methods` (line 10) creates database 
tables and updates them when the bot is restarted 
3. After pressing the start button by the user, the `send_basic_greeting` function  
from `handlers.default_handlers.handler` (line 16) is called, which  adds the user to the log file, 
displays the greeting and `menu_button` (from `keyboards.reply.menu_button`, line 7)
4. After clicking on the menu button, the `send_answer` function from `handlers.default_handlers.handlers` (line 159) 
is called, which calls the `send_greeting` function from `utils.misk.answers.answers_for_states.answers` (line 12),
which in turn calls the `commands_keyboard` function from `keyboards.inline.inline_keyboards` (line 11), after that 
a list of available commands is displayed on the screen. The `delete_previous_message` function is called 
from `handlers.handlers_for_request_and_after.handlers` (line 516), which deletes the previous inline keyboard 
if there is one
5. Depending on the command entered, the corresponding function is called from `handlers.default_handlers.handlers`:
   * `/lowprice` - `command_low_price` function from `handlers.default_handlers.handlers` (line 74) is called
   * `/highprice` - `command_high_price` function from `handlers.default_handlers.handlers` (line 96) is called
   * `/bestdeal` - `command_best_deal` function from `handlers.default_handlers.handlers` (line 118) is called
   * `/history` - `command_history` function from `handlers.default_handlers.handlers` (line 141) is called




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
button to get information about all available bot commands.
* `/hello-world` – displays a message that the world also welcomes
the user
###### note:
    you can only enter manually at any time
### Getting started
#### To launch the bot, you need:
* Installed Python interpreter version 3.8;
* All packages from requirements.txt
(enter in the console`pip install -r requirements.txt`, having previously activated the 
virtual environment);
* Create a file.env in the project directory where you save RAPIDAPI_KEY and token from your bot
(example file in .env.template).


