from aiogram import types
from loader import dp, db
from data.long_messages import long_messages
from data.functions import AssCore
from filters import IsGroup
from utils.set_rate_limit import rate_limit


@dp.message_handler(IsGroup(), commands="ass")
async def ass(message: types.Message):
    """
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    """
    
    group_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    ass_info = db.execute(query, fetchone=True)

    # if user exists in database
    if ass_info is None:  # if user didn't be registered in the game
        if username is None:  # if user doesn't have username
            username = first_name
        ass_info = AssCore((user_id, username, first_name, 0, 0, 0, 0, 0))

        query = """
            INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted, luck_timeleft)
            VALUES (?,?,?,?,?,?,?,?)
        """ % group_id
        args = (user_id, username, first_name, 0, 0, 0, 0, 0)
        db.execute(query, args, commit=True)

        await message.reply(
            "👋 Вітаю в нашій когорті, хлопче/дівчино!\n"
            + ass_info.ass_main(message, group_id))
    else:
        ass_info = list(ass_info)
        if ass_info[1] != username or ass_info[2] != first_name:

            if ass_info[1] != username:
                ass_info[1] = username

            if ass_info[2] != first_name:
                ass_info[2] = first_name

            query = "UPDATE `%d` SET username='%s', name='%s' WHERE user_id=%d" % \
                    (group_id, username, first_name, user_id)
            db.execute(query, commit=True)

        from time import time

        ass_info = AssCore(ass_info)

        if ass_info.blacklisted:  # if already blacklisted
            await message.reply("💢 %s, дружок, ти вже награвся, шуруй звідси." % first_name)
        else:  # if not blacklisted
            if int(time()) >= ass_info.endtime:  # if last_time already pasted
                await message.reply(ass_info.ass_main(message, group_id))
            else:
                if ass_info.spamcount == 4:  # if spamcount == 4 -> blacklisted
                    query = """
                        UPDATE `%d` SET blacklisted=1, length=0 WHERE user_id=%d
                    """ % (group_id, user_id)
                    db.execute(query, commit=True)

                    await message.reply(first_name + long_messages["spam"])
                else:
                    await message.reply(ass_info.ass_main(message, group_id))


@dp.message_handler(IsGroup(), commands="luck")
async def is_lucky(message: types.Message):
    """
    This command is try user's luck
    If user wins, user will get 200% of its length
    If user fails, user will last 60% of its length
    """
    # basic information
    
    group_id = message.chat.id
    user_id = message.from_user.id
    firstname = message.from_user.first_name

    # if a group wasn't registered
    query = """
        SELECT luck_timeleft, length, spamcount FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)
    
    inf = db.execute(query, fetchone=True)

    if inf is None:
        await message.reply("⛔️ Ти не зарегестрований у грі: пиши /ass")
        return
    else:
        luck_timeleft, length, spamcount = inf

    # if a user's length is too small
    if length < 100:
        await message.reply("⛔️ Як підростеш до 100 см, тоді і повертайся")
        return
    
    # check timeleft
    from time import time

    if luck_timeleft < time():
        # if time already passed -> allow play again
        # else deny it
        from random import randint, choice

        # chance of win
        winrate = 50
        k_win = 2  # 200%
        k_fail = 0.5   # 50%

        if winrate >= randint(1, 100):
            from data.emojis import LUCK_win_emojis

            await message.reply(
                "<b>%s ОТРИМАВ ВИГРАШ!</b> 📈\n\n"
                "%s Твій приз: %d см\n"
                "Продовжуй грати через неділю!"
                % (firstname, choice(LUCK_win_emojis), length * k_win - length))
            
            length *= k_win
        
        else:
            from data.emojis import LUCK_fail_emojis

            await message.reply(
                "<b>%s ПРОГРАВ!</b>! 📉\n\n"
                "%s Ти програв: %d см\n"
                "Продовжуй грати через неділю!"
                % (firstname, choice(LUCK_fail_emojis), length * k_fail))
            
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
        from math import ceil
        # define time left
        days_left = ceil(int(luck_timeleft - time()) / 86400)
        # answer with a count of days
        if days_left == 1:
            await message.reply("⛔️ Неділя ще не пройшла! Залишився 1 день.")
        else:
            await message.reply("⛔️ Неділя ще не пройшла! Залишилося %d д." % days_left)
        # increment spamcount and write it
        spamcount += 1
        query = """
            UPDATE `%d` SET spamcount=%d WHERE user_id=%d
        """ % (group_id, spamcount, user_id)
        db.execute(query, commit=True)


# a user leaves the game
@rate_limit(120)
@dp.message_handler(IsGroup(), commands="leave")
async def leave(message: types.Message):
    group_id = message.chat.id
    user_id = message.from_user.id
    
    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (group_id, user_id)

    ass_info = db.execute(query, fetchone=True)

    if not ass_info or ass_info is None:
        await message.answer("⛔️ Ти не зарегестрований у грі!")
        return

    ass_info = AssCore(ass_info)
    if ass_info.blacklisted:  # if user is blacklisted
        await message.reply("⛔️ Ні, дружок, таке не проканає 😏")
    else:  # if user isn't blacklisted
        query = """
            DELETE FROM `%d` WHERE user_id=%d
        """ % (group_id, user_id)
        db.execute(query, commit=True)
        await message.reply("✅ Ти покинув гру! Шкода такий гарний зад.")


# show statistics of playing user
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
        await message.reply("⛔️ Нема гравців! Стань першим!")
        return

    output_message = "📊 Рейтинг гравців:\n\n"

    from data.emojis import STATISTIC_top_emojis

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

    await message.reply(output_message)
