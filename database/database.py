from peewee import *


db = SqliteDatabase('hotels.db')


class BaseModel(Model):
    """The base class from which all tables inherit
    current database"""

    class Meta:
        """A class with database metadata

        :param: db: name of the current database
        :type: db: database object"""

        database = db


class HotelsSearchingDataBase(BaseModel):
    """A class containing database table fields with the user's chat id,
    its entered commands, the date of introduction and the result

    :param: user_id:  unique chat id
    :type: user_id:  integer (IntegerField)
    :param: command:  entered command
    :type: command: string (CharField)
    :param: date_of_command: date and time of the command call
    :type: date_of_command: datetime object
    :param: result_of_command: saved result of the entered command
    :type: result_of_command: ПОДУМАТЬ!!!!!!
    """

    user_id = IntegerField()
    command = CharField()
    date_of_command = DateTimeField()
    result_of_command = 'ПОДУМАТЬ !!!!!!'


HotelsSearchingDataBase.create_table()
