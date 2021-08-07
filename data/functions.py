from aiogram import types


class ass_info_obj:
    """
    Used for better understanding ass_info
    """

    def __init__(self, ass_info: tuple):
        self.id = ass_info[0]
        self.username = ass_info[1]
        self.name = ass_info[2]
        self.length = ass_info[3]
        self.endtime = ass_info[4]
        self.spamcount = ass_info[5]
        self.blacklisted = ass_info[6]
        self.luck_timeleft = ass_info[7]


def user_input(message: types.Message, command: str) -> str:
    text = message.text.replace(command + " ", "").strip()
    if command in text or command == "":
        return ""
    return text


def ass_main(message: types.Message, ass_info: [list, tuple], db, group_id: int) -> str:
    """
    This function is backend part of function `ass`

    :param message:  object message from handler
    :param ass_info: Information about user from a database
    :param db: Yeah, it's a database
    :param group_id: Yeah, that's a group id
    :return:         Send to a database an query which change data.
    """

    ass_info = ass_info_obj(ass_info)

    from time import time

    if ass_info.endtime > int(time()):
        last_time = ass_info.endtime - int(time())

        hours = int(last_time / 3600)
        last_time -= hours * 3600

        minutes = int(last_time / 60)

        # if user doesn't have username we set to username firstname
        if message.from_user.username is None:
            ass_info.username = message.from_user.first_name
        else:
            ass_info.username = "@" + message.from_user.username

        # append time to wait
        if hours == 0:
            if minutes == 0:
                output_message = (
                    "{0}, готую вимірювальні пристрої, зачекай хвильку".format(ass_info.username, minutes)
                )
            else:
                output_message = (
                    "{0}, ти вже грав! Зачекай {1} хв.".format(ass_info.username, minutes)
                )
        else:
            if minutes == 0:
                output_message = (
                    "{0}, ти вже грав! Зачекай {1} год.".format(ass_info.username, hours)
                )
            else:
                output_message = (
                    "{0}, ти вже грав! Зачекай {1} год. {2} хв.".format(ass_info.username, hours, minutes)
                )

        db.execute("""
            UPDATE `{0}` SET spamcount={1} WHERE user_id={2}
        """.format(group_id, ass_info.spamcount + 1, ass_info.id))
    else:

        # TODO: Make message which will be sent when user achieve some aim
        # For example:
        # 200 см - "Фіга вона велечезна"
        # 400 см - "Хай впаде на мене метеорит"
        # etc.

        from random import randint

        tmp_length = randint(-8, 15)

        if message.from_user.username is None:
            ass_info.username = message.from_user.first_name
        else:
            ass_info.username = "@" + message.from_user.username

        output_message = "{0}, твоя дупця ".format(ass_info.username)

        if tmp_length == 0:
            output_message += "не змінила розміру. "
        elif tmp_length > 0:
            output_message += (
                "підросла на {0} см! Зараз твоя дупця прям бомбезна. ".format(tmp_length)
            )
        elif tmp_length < 0:
            if not ass_info.length - tmp_length <= 0:
                output_message += (
                    "зменшилась на {0} см! Зараз твоя дупця вже не файна. ".format(tmp_length * -1)
                )

        ass_info.length = ass_info.length + tmp_length

        if ass_info.length <= 0:
            ass_info.length = 0
            output_message += "Зараз ти не маєш заду. "
        else:
            output_message += "\nНаразі ваша дупенція становить: {0} см. ".format(ass_info.length)

        end_time = int(time()) + randint(3600, 72000)  # from 1 hour to 20 hours
        last_time = end_time - int(time())

        if last_time >= 0:
            minutes = (last_time // 60) - (last_time // 3600) * 60
            hours = last_time // 3600
        else:
            minutes = ((last_time // 60) - (last_time // 3600) * 60) * -1
            hours = last_time // 3600 * -1

        output_message += "Продовжуй грати через {0} год., {1} хв.".format(hours, minutes)

        db.execute("""
                UPDATE `{0}` SET length={1}, endtime={2}, spamcount=0 WHERE user_id={3}
            """.format(group_id, ass_info.length, end_time, ass_info.id))

    return output_message
