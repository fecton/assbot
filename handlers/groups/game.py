from aiogram import types
from aiogram.utils.markdown import bold, italic, code
from aiogram.utils.markdown import escape_md as esc
from time import time
from math import ceil
from random import randint, choice

from loader import dp, db
from data.long_messages import long_messages
from data.functions import AssCore
from filters import IsGroup
from utils.set_rate_limit import rate_limit
from time import time
from data.config import USER_RATE_LIMIT

from data.emojis import LUCK_win_emojis
from data.emojis import LUCK_fail_emojis
from data.emojis import STATISTIC_top_emojis


@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(IsGroup(), commands="ass")
async def ass(message: types.Message):
    """
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    """
    
    # takes user info from message
    group_id   = message.chat.id
    user_id    = message.from_user.id
    username   = message.from_user.username
    first_name = message.from_user.first_name

    # combine sql query and run 
    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    ass_info = db.execute(query, fetchone=True)

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

        t = "👋 Вітаю в нашій когорті, хлопче/дівчино!\n" + ass_info.ass_main(message, group_id)

        await message.reply(esc(t))
    else:
        # else update him!
        ass_info = AssCore(ass_info)
        # ass_info = list(ass_info)
        if ass_info.username != username or ass_info.name != first_name:
            if ass_info.username != username:
                ass_info.username = username

            if ass_info.name != first_name:
                ass_info.name = first_name

            query = "UPDATE `%d` SET username='%s', name='%s' WHERE user_id=%d" % \
                    (group_id, username, first_name, user_id)
            db.execute(query, commit=True)


        if ass_info.blacklisted:  
            t = "💢 %s, дружок, ти вже награвся, шуруй звідси" % first_name
            await message.reply(esc(t))
        else:  
            if int(time()) >= ass_info.endtime:  # if last_time already pasted
                t = esc(ass_info.ass_main(message, group_id))
                await message.reply(t)
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

            await message.reply(esc(t)


@rate_limit(USER_RATE_LIMIT*10)
@dp.message_handler(IsGroup(), commands="luck")
async def is_lucky(message: types.Message):
    """
    This command is try user's luck
    If user wins, user will get 200% of its length
    If user fails, user will last 60% of its length
    """
    
    group_id = message.chat.id
    user_id = message.from_user.id
    firstname = message.from_user.first_name

    # if a group wasn't registered
    query = """
        SELECT luck_timeleft, length, spamcount FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)
    
    inf = db.execute(query, fetchone=True)

    if inf is None:
        t = "Ти не зарегестрований у грі: пиши /ass"
        await message.reply(esc(t))
        return
    else:
        luck_timeleft, length, spamcount = inf

    # if a user's length is too small
    
    if length < 100:
        t = "Дружок, твоя дупця ще не достатньо величезна ✌️, повертайся після 100 см"
        await message.reply(esc(t))
        return
    
    # check timeleft
    if luck_timeleft < time():
        # if time already passed -> allow play again
        # else deny it

        # chance of win
        winrate = 45
        k_win = 2  # 200%
        k_fail = 0.5   # 50%

        if winrate >= randint(1, 100):
            t = (f"{bold(firstname + ' ОТРИМАВ ВИГРАШ!')} 📈\n\n" + 
                esc("%s Твій приз: %d см\n" % (choice(LUCK_win_emojis), length * k_win - length)) +
                esc("Продовжуй грати через неділю!")
                )

            await message.reply(t)
            
            length *= k_win
        else:
            t = (f"{bold(firstname + ' ПРОГРАВ!')} 📉\n\n" +
                esc("%s Ти програв: %d см\n" % (choice(LUCK_fail_emojis), length * k_fail)) +
                esc("Продовжуй грати через неділю!")
                )

            await message.reply(t)
            
            length -= length * k_fail

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

        output_message = "Козаче, тиждень ще не пройшов! Спробуй через " + f"{'1 день' if days_left == 1 else f'{days_left} дні'}"
    
        await message.reply(esc(output_message))

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
    group_id = message.chat.id
    user_id = message.from_user.id
    
    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    ass_info = db.execute(query, fetchone=True)

    if ass_info is None:
        t = "Ти не зарегестрований у грі!"
        await message.answer(esc(t))
        return

    ass_info = AssCore(ass_info)
    if ass_info.blacklisted:  # if user is blacklisted
        t = "Ні, дружок, таке не проканає 😏"
        await message.reply(esc(t))
    else:  # if user isn't blacklisted
        query = """
            DELETE FROM `%d` WHERE user_id=%d
        """ % (group_id, user_id)
        db.execute(query, commit=True)
        t = "Ти покинув гру! Шкода такий гарний зад"

        await message.reply(esc(t))


# show statistics of playing user
@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(IsGroup(), commands="statistic")
async def statistic(message: types.Message):
    """
    This handler make and send an output message with user descending users by length
    """
    
    query = """
        SELECT * FROM `%d` ORDER BY blacklisted ASC, length DESC
    """ % message.chat.id

    users_data = db.execute(query, fetchall=True)
    
    if not users_data:
        t = "⛔️ Нема гравців! Стань першим!"
        await message.reply(esc(t))
        return

    output_message = "📊 Рейтинг гравців:\n\n"

    i = 0

    for user_data in users_data:
        # user_data = list(user_data)

        # (user_id, username, fisrtname, length, endtime, spamcount, blacklisted)
        user_data = AssCore(user_data)
        
        if user_data.blacklisted:
            output_message += "💢 {1} залишився без дупи через спам\n".format(i, user_data.name)
            continue

        if i < len(STATISTIC_top_emojis):  # with emojis
            if i == 0:  # if is king
                if user_data.length == 0:  # "👑  Безжопий царь {username}"
                    output_message += "     %s Безжопий царь %s\n\n" % (STATISTIC_top_emojis[i]+" ", user_data.name)
                else:                     # "👑  Царь {username}"
                    output_message += "     %s Царь %s — %d см\n\n" % (
                        STATISTIC_top_emojis[i], user_data.name, user_data.length
                    )
            else:
                output_message += STATISTIC_top_emojis[i] + " "
                if not user_data.length:
                    output_message += "{0}. {1} — не має сіднички\n".format(i, user_data.name)
                else:
                    output_message += "{0}. {1} — {2} см\n".format(i, user_data.name, user_data.length)
        else:  # without emojis
            if not user_data.length:
                output_message += "{0}. {1} — не має сіднички\n".format(i, user_data.name)
            else:
                output_message += "{0}. {1} — {2} см\n".format(i, user_data.name, user_data.length)
        i += 1

    await message.reply(esc(output_message))
