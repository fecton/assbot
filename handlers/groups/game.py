import sqlite3
import asyncio

from aiogram import types
from aiogram.utils.markdown import bold, italic, code
from aiogram.utils.markdown import escape_md as esc

from loader import dp, db

from math import ceil
from random import randint, choice
from filters import IsGroup
from time import time

from utils.set_rate_limit import rate_limit
from utils.db_core import DbCore

from data.config import USER_RATE_LIMIT, IS_DEBUG, long_messages, LUCK_win_emojis, LUCK_fail_emojis, STATISTIC_top_emojis
from data.functions import AssCore

errors_m = long_messages["errors"]


async def answer(message: types.Message, t: str, delay: int = 3):
    """
    message.answer with timeout and auto deletion the message

    message: a message taked by handler
    t: text
    delay: timeout for message
    """

    sentM = (await message.answer(t))
    await asyncio.sleep(delay)
    await sentM.delete()


async def reply(message: types.Message, t: str, delay: int = 3):
    """
    message.reply with timeout and auto deletion the message

    message: a message taked by handler
    t: text
    delay: timeout for message
    """

    sentM = (await message.reply(t))
    await asyncio.sleep(delay)
    await sentM.delete()


@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(IsGroup(), commands="ass")
async def ass(message: types.Message):
    """
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    """

    ass_m = long_messages["ass"]

    # takes user info from message
    group_id   = message.chat.id
    user_id    = message.from_user.id
    username   = message.from_user.username
    first_name = message.from_user.first_name

    # combine sql query and run 
    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    try:
        ass_info = db.execute(query, fetchone=True)
    except sqlite3.OperationalError:
        db.create_group_table(group_id)
        ass_info = None

    # if user does not exist -> add him
    if ass_info is None:
        if username is None:
            username = first_name

        ass_info = AssCore((user_id, username, first_name, 0, 0, 0, 0, 0))

        query = """
            INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted, luck_timeleft)
            VALUES (?,?,?,?,?,?,?,?)
        """ % group_id
        args = (user_id, username, first_name, 0, 0, 0, 0, 0)
        db.execute(query, args, commit=True)

        t = esc(ass_m["first_start"] + ass_info.ass_main(message, group_id))

        await reply(message, t)
    else:
        # else update him!
        ass_info = AssCore(ass_info)

        if ass_info.username != username or ass_info.name != first_name:
            if ass_info.username != username:
                ass_info.username = username

            if ass_info.name != first_name:
                ass_info.name = first_name

            query = "UPDATE `%d` SET username='%s', name='%s' WHERE user_id=%d" % \
                    (group_id, username, first_name, user_id)
            db.execute(query, commit=True)


        if ass_info.blacklisted:
            t = ass_m["blacklisted"] % first_name
        else:
            if int(time()) >= ass_info.endtime:  # if last_time already pasted
                t = ass_info.ass_main(message, group_id)
            else:
                # if spamcount == 5 -> blacklisted
                if ass_info.spamcount == 5:
                    query = """
                        UPDATE `%d` SET blacklisted=1, length=0 WHERE user_id=%d
                    """ % (group_id, user_id)
                    db.execute(query, commit=True)

                    t = first_name + long_messages["spam"]
                else:
                    t = ass_info.ass_main(message, group_id)

        t = esc(t)

        await reply(message, t)

@rate_limit(USER_RATE_LIMIT*10)
@dp.message_handler(IsGroup(), commands="luck")
async def is_lucky(message: types.Message):
    """
    This command is try user's luck
    If user wins, user will get 200% of its length
    If user fails, user will last 60% of its length
    """

    luck_m = long_messages["luck"]

    group_id = message.chat.id
    user_id = message.from_user.id
    firstname = message.from_user.first_name

    # if a group wasn't registered
    query = """
        SELECT luck_timeleft, length, spamcount FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    try:
        inf = db.execute(query, fetchone=True)
    except sqlite3.OperationalError:
        db.create_group_table(group_id)
        inf = None

    if inf is None:
        t = esc(errors_m["not_registered"])
        await reply(message, t)
        return
    else:
        luck_timeleft, length, spamcount = inf

    # if a user's length is too small
    if length < 100 and not IS_DEBUG:
        t = esc(long_messages["luck"]["tiny_ass"])
        await reply(message, t)
        return
    # check timeleft
    if luck_timeleft < time() or IS_DEBUG:

        winrate = 45
        k_win = 2  # 200%
        k_fail = 0.5   # 50%

        if winrate >= randint(1, 100):
            t = (esc(luck_m["won"]) % (bold(firstname), choice(LUCK_win_emojis), length*k_win-length))

            length *= k_win
        else:
            t = (esc(luck_m["fail"]) % (bold(firstname), choice(LUCK_fail_emojis), length*k_fail))

            length -= length * k_fail

        t += esc(luck_m["continue_after_a_week"])
        await reply(message, t)

        # write length to db
        query = """
            UPDATE `%d` SET length=%d WHERE user_id=%d
        """ % (group_id, length, user_id)
        db.execute(query, commit=True)

        # define and write timeleft to db
        luck_timeleft = int(time()) + 604800  # +week
        query = """
            UPDATE `%d` SET luck_timeleft=%d WHERE user_id=%d
        """ % (group_id, luck_timeleft, user_id)
        db.execute(query, commit=True)

    else:
        # define time left
        days_left = ceil(int(luck_timeleft - time()) / 86400)
        # answer with a count of days

        t = esc(luck_m["time_isnt_passed"] + f"{'1 день' if days_left == 1 else f'{days_left} дні'}")

        await reply(message, t)

        # increment spamcount and write it
        spamcount += 1
        query = """
            UPDATE `%d` SET spamcount=%d WHERE user_id=%d
        """ % (group_id, spamcount, user_id)
        db.execute(query, commit=True)


# a user leaves the game
@rate_limit(USER_RATE_LIMIT*3)
@dp.message_handler(IsGroup(), commands="leave")
async def leave(message: types.Message):
    leave_m = long_messages["leave"]

    group_id = message.chat.id
    user_id = message.from_user.id
    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    ass_info = db.execute(query, fetchone=True)

    if ass_info is None:
        t = esc(long_messages["errors"]["not_registered"])

        await answer(message, t)
        return

    ass_info = AssCore(ass_info)
    if ass_info.blacklisted:  # if user is blacklisted
        t = esc(leave_m["nope"])
    else:  # if user isn't blacklisted
        query = """
            DELETE FROM `%d` WHERE user_id=%d
        """ % (group_id, user_id)
        db.execute(query, commit=True)

        t = esc(leave_m["so_sad"])

    await reply(message, t)


# show statistics of playing user
@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(IsGroup(), commands="statistic")
async def statistic(message: types.Message):
    """
    This handler make and send an output message with user descending users by length
    """

    stat_m = long_messages["statistic"]

    query = """
        SELECT * FROM `%d` ORDER BY blacklisted ASC, length DESC
    """ % message.chat.id

    users_data = db.execute(query, fetchall=True)

    if not users_data:
        t = esc(long_messages["errors"]["no_players"])
        await reply(message, t)
        return

    output_message = stat_m["header"]

    i = -1

    for user_data in users_data:
        i += 1

        # (user_id, username, fisrtname, length, endtime, spamcount, blacklisted)
        user_data = AssCore(user_data)

        if user_data.blacklisted:
            output_message = (stat_m["blacklisted"] % user_data.name)
        elif i == 0:
            if user_data.length == 0:
                output_message += (stat_m["zero_king"] % (STATISTIC_top_emojis[i]+" ", user_data.name))
            else:
                output_message += (stat_m["king"] % (STATISTIC_top_emojis[i], user_data.name, user_data.length))

            continue
        elif i < len(STATISTIC_top_emojis):
            output_message += STATISTIC_top_emojis[i] + " "

        if user_data.length == 0:
            output_message += (stat_m["zero_ass"] % (i, user_data.name))
        else:
            output_message += (stat_m["positive_ass"] % (i, user_data.name, user_data.length))

    output_message = esc(output_message)
    await reply(message, output_message)
