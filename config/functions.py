from typing import Union
from aiogram import types
from time import time
from random import randint

from config import IS_DEBUG, long_messages
from utils import db_core

assmain_m = long_messages["ass_main"]


class AssCore:
    """
    Used for better understanding ass_info
    """

    def __init__(self, ass_info: Union[tuple, list]):

        self.id             = ass_info[0]
        self.username       = ass_info[1]
        self.name           = ass_info[2]
        self.length         = ass_info[3]
        self.endtime        = ass_info[4]
        self.spamcount      = ass_info[5]
        self.blacklisted    = ass_info[6]
        self.luck_timeleft  = ass_info[7]

        self.ass_info = ass_info

    def ass_main(self, message: types.Message, group_id: int) -> str:
        """
        This function is backend part of function `ass`

        :param message:  object message from handler
        :param group_id: Yeah, that's a group id
        :return:         Send to a database an query which change data.
        """

        db = db_core()

        if self.endtime > int(time()) and not IS_DEBUG:
            last_time = self.endtime - int(time())

            hours = int(last_time / 3600)
            last_time -= hours * 3600

            minutes = int(last_time / 60)

            # if user doesn't have username we set to username firstname
            if message.from_user.username is None:
                self.username = message.from_user.first_name
            else:
                self.username = "@" + message.from_user.username

            # append time to wait
            if hours == 0:
                if minutes == 0:
                    output_message = (assmain_m["almost_zero"] % (self.username))
                else:
                    output_message = (assmain_m["hours_zero"] % (self.username, minutes))
            else:
                if minutes == 0:
                    output_message = (assmain_m["minutes_zero"] % (self.username, hours))
                else:
                    output_message = (assmain_m["hours_minutes"] % (self.username, hours, minutes))

            db.execute("""
                UPDATE `%d` SET spamcount=%d WHERE user_id=%d
            """ % (group_id, self.spamcount + 1, self.id), commit=True)
        else:

            tmp_length = randint(-8, 15)

            if message.from_user.username is None:
                self.username = message.from_user.first_name
            else:
                self.username = "@" + message.from_user.username

            output_message = assmain_m["your_ass"] % self.username

            if tmp_length == 0:
                output_message += assmain_m["didn't_change"]
            elif tmp_length > 0:
                output_message += (assmain_m["icreased"] % tmp_length)
            elif tmp_length < 0:
                if self.length + tmp_length <= 0:
                    output_message += assmain_m["disappeared"]
                else:
                    output_message += (assmain_m["decreased"] % (tmp_length * -1))

            self.length = self.length + tmp_length

            if self.length <= 0:
                self.length = 0
                output_message += assmain_m["equals_zero"]
            else:
                output_message += (assmain_m["greater_than_zero"] % self.length)

            self.endtime = int(time()) + randint(3600, 72000)  # from 1 hour to 20 hours
            last_time = self.endtime - int(time())

            if last_time >= 0:
                minutes = (last_time // 60) - (last_time // 3600) * 60
                hours = last_time // 3600
            else:
                minutes = ((last_time // 60) - (last_time // 3600) * 60) * -1
                hours = last_time // 3600 * -1

            output_message += "Продовжуй грати через {0} год. {1} хв.".format(hours, minutes)

            db.execute("""
                    UPDATE `%d` SET length=%d, endtime=%d, spamcount=0 WHERE user_id=%d
                """ % (group_id, self.length, self.endtime, self.id), commit=True)

        return output_message


def user_input(message: types.Message, command: str) -> str:
    """
    This function returns users output after command
    Example: "/ban 23432422"
        Returns: "23432422"
    :param message: types.Message object gotten from handler
    :param command: This is a commands which will be deleted with a space from message.text
    """
    text = message.text.replace(command + " ", "").strip()
    if command in text or command == "":
        return ""
    return text
