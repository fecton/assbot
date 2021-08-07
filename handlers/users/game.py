import sqlite3
from aiogram import types
from loader import dp
from data.config import DB_NAME, long_messages
from data.functions import ass_info_obj, ass_main


@dp.message_handler(commands="ass")
async def ass(message: types.Message):
    """
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    """

    if message.chat.type == "private":
        await message.answer("⛔️ Працює лишу у групах!")
        return

    group_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    db = sqlite3.connect(DB_NAME)

    cursor = db.execute("""
    SELECT * FROM `{0}` WHERE user_id={1}
    """.format(group_id, user_id))

    ass_info = cursor.fetchone()

    # if user exists in database
    if ass_info is None:  # if user didn't be registered in the game
        if username is None:  # if user doesn't have username
            username = first_name
        ass_info = (user_id, username, first_name, 0, 0, 0, 0, 0)

        db.execute("""
            INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted, luck_timeleft)
            VALUES (?,?,?,?,?,?,?,?)
        """ % group_id, ass_info)

        await message.reply(
            "👋 Вітаю в нашій когорті, хлопче/дівчино!\n"
            + ass_main(message, ass_info, db, group_id))
    else:
        ass_info = list(ass_info)
        if ass_info[1] != username or ass_info[2] != first_name:

            if ass_info[1] != username:
                ass_info[1] = username

            if ass_info[2] != first_name:
                ass_info[2] = first_name

            db.execute(
                "UPDATE `%d` SET username='%s', name='%s' WHERE user_id=%d"
                % (group_id, username, first_name, user_id)
            )

        from time import time
        is_blacklisted = ass_info[6]
        endtime = ass_info[4]
        spamcount = ass_info[5]
        if is_blacklisted:  # if already blacklisted
            await message.reply("💢 %s, дружок, ти вже награвся, шуруй звідси." % first_name)
        else:  # if not blacklisted
            if int(time()) >= endtime:  # if last_time already pasted
                await message.reply(ass_main(message, ass_info, db, group_id))
            else:
                if spamcount == 5:  # if spamcount == 5 -> blacklisted
                    db.execute("""
                        UPDATE `{0}` SET blacklisted=1, length=0 WHERE user_id={1}
                    """.format(group_id, user_id))
                    await message.reply(first_name + long_messages["spam"])
                else:
                    await message.reply(ass_main(message, ass_info, db, group_id))

    db.commit()
    db.close()


@dp.message_handler(commands="luck")
async def is_lucky(message: types.Message):
    """
    This command is try user's luck
    If user wins, user will get 200% of its length
    If user fails, user will last 60% of its length
    """

    if message.chat.type == "private":
        await message.answer("⛔️ Працює лишу у группах!")
        return

    db = sqlite3.connect(DB_NAME)

    group_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        db.execute("SELECT * FROM `%d`" % group_id)
    except sqlite3.OperationalError:
        await message.reply("⛔️ Ти не зарегестрований у грі: пиши /ass")
        db.close()
        return

    # try:
    inf = db.execute(
        "SELECT luck_timeleft, length, spamcount FROM `%d` WHERE user_id=%d" % (group_id, user_id)).fetchone()

    if inf is None:
        await message.reply("⛔️ Ти не зарегестрований у грі: пиши /ass")
        db.close()
        return
    else:
        luck_timeleft, length, spamcount = inf

    if length < 100:
        await message.reply("⛔️ Твоя сідничка дуже мала! (мін. 100 см)")
        return
    
    from time import time

    if luck_timeleft < time():
        from random import randint, choice
        winrate = 30

        if winrate >= randint(1, 100):
            from data.emojis import LUCK_fail_emojis

            await message.reply(
                "@%s ОТРИМАВ ВИГРАШ! 📈\n%s Ти мене обікрав, забирай свій приз: %d см.\n"
                "Зараз у тебе: %d см.\nПродовжуй грати через неділю!"
                % (username, choice(LUCK_fail_emojis), length, length * 2))
            length *= 2
        else:
            from data.emojis import LUCK_fail_emojis

            await message.reply(
                "@%s ПРОГРАВ %d см! 📉\n%s Сьогодні явно не твій день :)"
                "\nЗараз у тебе: %d см.\nПродовжуй грати через неділю!"
                % (username, length, choice(LUCK_fail_emojis), length - length * 0.6))
            length -= length * 0.5

        db.execute("UPDATE `%d` SET length=%d WHERE user_id=%d" % (group_id, length, user_id))

        luck_timeleft = int(time()) + 604800  # +week
        db.execute("UPDATE `%d` SET luck_timeleft=%d WHERE user_id=%d" % (group_id, luck_timeleft, user_id))
        db.commit()
    else:
        from math import ceil
        days_left = ceil(int(luck_timeleft - time()) / 86400)

        if days_left == 1:
            await message.reply("⛔️ Завтра ми відкриємо для тебе наші двері!")
        else:
            await message.reply("⛔️ Неділя ще не пройшла! Залишилося %d д." % days_left)
        spamcount += 1
        db.execute("UPDATE `%d` SET spamcount=%d WHERE user_id=%d" % (group_id, spamcount, user_id))

    db.close()


# a user leaves the game
@dp.message_handler(commands="leave")
async def leave(message: types.Message):
    if message.chat.type == "private":  # if message was gotten in a group
        await message.answer("⛔️ Працює лише у групах!")
        return

    db = sqlite3.connect(DB_NAME)

    cursor = db.execute("""
    SELECT * FROM `{0}` WHERE user_id={1}
    """.format(message.chat.id, message.from_user.id))

    ass_info = ass_info_obj(cursor.fetchone())

    if ass_info:  # if user isn't registered
        if ass_info.blacklisted:  # if user is blacklisted
            await message.reply("⛔️ Ні, дружок, таке не проканає 😏")
        else:  # if user isn't blacklisted
            db.execute("""
                DELETE FROM `{0}` WHERE user_id={1}
            """.format(message.chat.id, message.from_user.id))
            await message.reply("✅ Ти покинув гру! Шкода такий гарний зад.")
    else:  # if user isn't registered
        await message.reply("⛔️ Ти не зарегестрований у грі!")
    db.commit()
    db.close()


# show statistics of playing user
@dp.message_handler(commands="statistic")
async def statistic(message: types.Message):
    """
    This handler make and send an output message with user descending users by length
    """

    if message.chat.type == "private":
        await message.answer("⛔️ Працює лише у групах!")
        return

    db = sqlite3.connect(DB_NAME)
    try:
        cursor = db.execute("""
            SELECT * FROM `{0}` ORDER BY blacklisted ASC, length DESC
        """.format(message.chat.id))
        users_data = cursor.fetchall()
        db.close()
    except sqlite3.OperationalError:
        await message.reply("⛔️ Нема гравців! Стань першим!")
        db.close()
        return

    if not users_data:
        await message.reply("⛔️ Нема гравців! Стань першим!")
    else:
        output_message = "📊 Рейтинг гравців:\n\n"

        from data.emojis import STATISTIC_top_emojis

        i = 0

        for user_data in users_data:
            # user_data = list(user_data)

            # (user_id, username, fisrtname, length, endtime, spamcount, blacklisted)
            user_data = ass_info_obj(user_data)
            
            if user_data.blacklisted:
                output_message += "💢 {1} залишився без дупи через спам\n".format(i, user_data.name)
                continue

            if i < len(STATISTIC_top_emojis):  # with emojis
                if i == 0:  # if is king
                    if user_data.length == 0:
                        output_message += "     %s Безжопий царь %s\n\n" % (STATISTIC_top_emojis[i]+" ", user_data.name)
                    else:
                        output_message += "     %s Царь %s — %d см\n\n" % (
                            STATISTIC_top_emojis[i], user_data.name, user_data.length)
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
