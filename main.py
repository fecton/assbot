#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Open-Source AssBot 2021
# ------------------------------
#
# Made with love by Fecton
# https://github.com//fecton
#
# ------------------------------
# Enjoy using! ^_^

__version__ = '1.4'

import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from random  import randint, choice
from json    import loads
from time    import time
from math    import ceil
from os      import path

from config import *

DB_NAME = "list"

# initialization
bot = Bot(TOKEN)
dp  = Dispatcher(bot)

print("[+] Bot initialization was successfully!")


# if you want to read from json-file
content = loads(open("messages.json", "r", encoding="utf8").read())


class ass_info_obj:
    '''
    Used for better understanding ass_info
    '''
    def __init__(self, ass_info: tuple):
        self.id            = ass_info[0]
        self.username      = ass_info[1]
        self.name          = ass_info[2]
        self.length        = ass_info[3]
        self.endtime       = ass_info[4]
        self.spamcount     = ass_info[5]
        self.blacklisted   = ass_info[6]
        self.luck_timeleft = ass_info[7]


def user_input(message: types.Message, command: str) -> str:
    text = message.text.replace(command + " ", "").strip()
    if command in text or command == "":
        return ""
    return text


def ass_main(ass_info: list, db, group_id: int) -> str:
    '''
    This function is backend part of function `ass`

    :param ass_info: Information about user from a database
    :param database: Yeah, it's a database
    :param group_id: Yeah, that's a group id
    :return:         Send to a database an query which change data.
    '''

    # ass_info = ass_info_obj(ass_info)

    if ass_info.endtime > int(time()):
        last_time = ass_info.endtime - int(time())

        hours = int(last_time / 3600)
        last_time -= hours * 3600

        minutes = int(last_time / 60)

        if ass_info.username == ass_info.name: ass_info.username = ass_info.name
        else:                                  ass_info.username = "@" + ass_info.username

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

        tmp_length = randint(-8, 15)

        if ass_info.username == ass_info.name:
            ass_info.username = ass_info.name
        else:
            ass_info.username = "@" + ass_info.username

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

        if ass_info.length < 0:
            ass_info.length = 0
            output_message += "Зараз ти не маєш заду. "
        else:
            output_message += "\nНаразі ваша дупенція становить: {0} см. ".format(ass_info.length)


        end_time = int(time()) + randint(3600, 72000) # from 1 hour to 20 hours
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


if not path.exists(DB_NAME):
    # it created database if it doesn't exist + create tables
    db = sqlite3.connect(DB_NAME)
    db.execute("""
        CREATE TABLE `reports` (
            group_id    INTEGER        NOT NULL,
            group_name  VARCHAR(255)   NOT NULL,
            user_id     INTEGER        NOT NULL,
            username    VARCHAR(35)    NOT NULL,
            name        VARCHAR(255)   NOT NULL,
            message     TEXT           NOT NULL
        )
    """)
    print("[+] Report table was created successfully!")
    db.execute("""
        CREATE TABLE `groups_name` (
            group_id    INTEGER      NOT NULL,
            group_name  VARCHAR(255) NOT NULL
        )
    """)
    print("[+] Group's name table was created successfully!")

    db.commit()
    db.close()

else:
    print("[+] Everything is fine!")


@dp.message_handler(commands="ass")
async def ass(message: types.Message):
    '''
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    '''

    if message.chat.type != "private":
        group_id   = message.chat.id * -1
        user_id    = message.from_user.id
        username   = message.from_user.username
        first_name = message.from_user.first_name

        db = sqlite3.connect(DB_NAME)

        try:  # if group's table exists
            cursor = db.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            ass_info = cursor.fetchone()
        except sqlite3.OperationalError:
            # creating table with name by group_id

            db.execute("""
            CREATE TABLE `%d`(
                    user_id       INTEGER     PRIMARY KEY NOT NULL,
                    username      VARCHAR(35)             NOT NULL,
                    name          VARCHAR(255)            NOT NULL,
                    length        INTEGER                 NOT NULL,
                    endtime       INTEGER                 NOT NULL,
                    spamcount     INTEGER                 NOT NULL,
                    blacklisted   BOOLEAN                 NOT NULL,
                    luck_timeleft INTEGER                 NOT NULL
                );""" % group_id)

            print("[+] Table with name '%d' (%s) created successfully!" % (group_id, message.chat.title))

            cursor = db.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            
            ass_info = cursor.fetchone()

            if ass_info is not None:
                ass_info = ass_info_obj(cursor.fetchone())

            try:
                db.execute("""
                    INSERT INTO `groups_name` (group_id, group_name)
                    VALUES (?,?)
                """, (group_id, message.chat.title))

            except sqlite3.OperationalError:
                db.execute("""
                    CREATE TABLE `groups_name` (
                        group_id    INTEGER      NOT NULL,
                        group_name  VARCHAR(255) NOT NULL
                    )
                """)
                db.execute("""
                    INSERT INTO `groups_name` (group_id, group_name)
                    VALUES (?,?)
                """, (group_id, message.chat.title))

                print("[+] Table `groups_name` created and row was added successfully!")

        db.commit()

        # if user exists in database

        if ass_info is None:  # if user didn't be registered in the game
            if username is None:  # if user doesn't have username
                username = first_name
            userinfo = (user_id, username, first_name, 0, 0, 0, 0, 0)

            db.execute("""
                INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted, luck_timeleft)
                VALUES (?,?,?,?,?,?,?,?)
            """ % group_id, userinfo)

            ass_info = ass_info_obj(userinfo)

            await message.reply(f"👋 Вітаю в нашій когорті, хлопче/дівчино!\n" + ass_main(ass_info, db, group_id))
        else:
            ass_info = ass_info_obj(ass_info)
            if ass_info.blacklisted:  # if already blacklisted
                await message.reply("💢 %s, дружок, ти вже награвся, шуруй звідси." % first_name)
            else:  # if not blacklisted
                if int(time()) >= ass_info.endtime:  # if last_time already pasted
                    await message.reply(ass_main(ass_info, db, group_id))
                else:
                    if ass_info.spamcount == 5:  # if spamcount == 5 -> blacklisted
                        db.execute("""
                            UPDATE `{0}` SET blacklisted=1, length=0 WHERE user_id={1}
                        """.format(group_id, user_id))
                        await message.reply( first_name + content["spam"] )
                    else:
                        await message.reply(ass_main(ass_info, db, group_id))

        db.commit()
        db.close()


@dp.message_handler(commands="luck")
async def is_lucky(message: types.Message):
    '''
    Here must be documentation
    '''

    if message.chat.type == "private":
        await message.answer("⛔️ Працює лишу у группах!")
        return

    db = sqlite3.connect(DB_NAME)

    group_id  = message.chat.id * -1
    user_id   = message.from_user.id
    username  = message.from_user.username
    firstname = message.from_user.first_name 

    try:
        db.execute("SELECT * FROM `%d`" % group_id)
    except sqlite3.OperationalError:
        await message.reply("⛔️ Ти не зарегестрований у грі: пиши /ass")
        db.close()
        return

    #try:
    inf = db.execute("SELECT luck_timeleft, length, spamcount FROM `%d` WHERE user_id=%d" % (group_id, user_id)).fetchone()

    if inf is None:
        await message.reply("⛔️ Ти не зарегестрований у грі: пиши /ass")
        db.close()
        return
    else:
        luck_timeleft, length, spamcount = inf

    if length < 100:
        await message.reply("⛔️ Твоя сідничка дуже мала (мін. 100 см)!")
        return

    if luck_timeleft < time():
        winrate  = 10
        
        if winrate >= randint(1,100):
            good_emojis = ["😡", "🤬", "🤯", "😱", "😨", "😵", "👺", "😥", "😰", "😣", "😖", "😫", "😤", "😠", "🥺"]
            await message.answer("📈 Мене обікрали!\n%s Забирай свої сантиметри: %d см.\nЗараз у тебе: %d см.\nПродовжуй грати через неділю!" % (choice(good_emojis), length, length*2))
            length *= 2
        else:
            bad_emojis = ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "☺️", "😊", "🙂", "🙃", "😉", "😛", "😋", "😚", "🤩", "🥳", "😏"]
            await message.answer("📉 Чік -%d см.\n%s Сьогодні явно не твій день :)\nЗараз у тебе: %d см.\nПродовжуй грати через неділю!" % (length, choice(bad_emojis), length -  length * 0.6))
            length -= length * 0.6

        db.execute("UPDATE `%d` SET length=%d WHERE user_id=%d" % (group_id, length, user_id))

        luck_timeleft  = int(time()) + 604800 # +week
        db.execute("UPDATE `%d` SET luck_timeleft=%d WHERE user_id=%d" % (group_id, luck_timeleft, user_id))
        db.commit()
    else:
        days_left = ceil(int(luck_timeleft - time()) / 86400)

        if days_left == 1:  
            await message.reply("⛔️ Завтра ми відкриємо для тебе наші двері!")
        else:
            await message.reply("⛔️ Неділя ще не пройшла! Залишилося %d д." % days_left)
        spamcount += 1
        db.execute("UPDATE `%d` SET spamcount=%d WHERE user_id=%d" % (group_id, spamcount, user_id))

    db.close()

@dp.message_handler(commands="bl")
async def show_blacklisted_users(message: types.Message):
    '''
    This function shows all banned users in a group
    '''

    if message.from_user.id in SUPER_USERS:  # if is admin
        group_id = user_input(message, "/bl")

        if group_id == "":
            await message.reply("⛔️ Ти забув ввести ID группи!")
        else:
            if group_id == "self":
                group_id = message.chat.id*-1
            else:
                try:
                    group_id_tmp = int(group_id)
                except ValueError:
                    await message.reply("⛔️ Вибач, але не знаю такої групи.")
                    return

            db = sqlite3.connect(DB_NAME)
            try:
                cursor = db.execute("""
                    SELECT * FROM `{0}` WHERE blacklisted=1
                """.format(group_id))
                users_data = cursor.fetchall()
            except sqlite3.OperationalError:
                await message.reply("⛔️ Вибач, але не знаю такої групи.")
                db.close()
                return
            finally:
                db.close()

            if not users_data:
                await message.reply("✅ Нема заблокованих користувачів!")
            else:
                output_message  = f"👥 Group: <code>{group_id}</code>\n"
                output_message += "ID : USERNAME : NAME\n\n"

                users_count = 0
                for user_data in users_data:
                    users_count += 1
                    if user_data[1] == user_data[2]:
                        output_message += f"💢 {user_data[0]} :  {user_data[1]}\n"
                    else:
                        output_message += f"💢 {user_data[0]} :  @{user_data[1]} : {user_data[2]}\n"
                if users_count == 1:
                    output_message += "\n📌 Totally: 1 user"
                else:
                    output_message += "\n📌 Totally: %d users" % users_count
                await message.reply(output_message, parse_mode="HTML")


@dp.message_handler(commands="groups")
async def show_groups(message: types.Message):
    '''
    This function shows all registered in the game groups (its id and its name)
    '''

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        # cursorObj = database.cursor()
        # cursorObj.execute("SELECT name FROM sqlite_master WHERE type='table'")
        try:
            groups_info = db.cursor().execute("SELECT * FROM `groups_name`").fetchall()
        except sqlite3.OperationalError:
            print("[!] The table `groups_name` doesn't exist or was deleted, created new one")
            db.execute("""
                CREATE TABLE `groups_name` (
                    group_id    INTEGER      NOT NULL,
                    group_name  VARCHAR(255) NOT NULL
                )
            """)

            db.execute("""
                INSERT INTO `groups_name` (group_id, group_name)
                VALUES (?,?)
            """, (message.chat.id *-1, message.chat.title)
            )
            groups_info = db.cursor().execute("SELECT * FROM `groups_name`").fetchall()

        db.close()

        groups_dict = dict()

        for group in groups_info:
            groups_dict[group[0]] = group[1]

        output_message = "✅ __*TABLES*__\n"+"="*16+"\n"
        for key in groups_dict.keys():
            output_message += "`%s`" % str(key) + " : " + groups_dict[key] + "\n"

        await message.reply(output_message, parse_mode="Markdown")


# SHOW REPORTS FROM TABLE `reports` in simple form
@dp.message_handler(commands="reports")
async def show_reports(message: types.Message):
    '''
    This function show all rows from table `reports` and send it in one message
    '''

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        users = db.execute("SELECT * FROM `reports`").fetchall()

        db.close()

        if users:  # if users exist in group's table
            output_message = "USERNAME : NAME : MESSAGE\n\n"
            for user in users:
                output_message += f"🚩 {user[4]} : {user[5]}\n"
            await message.reply(output_message)
        else:
            await message.reply("⛔️ Ще нема звітів")


# SHOW REPORTS FROM TABLE `reports` in detailed form
@dp.message_handler(commands="dreports")
async def show_dreports(message: types.Message):
    '''
    This function show all rows from table `reports` and send it in one message
    '''

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        users = db.execute("SELECT * FROM `reports`").fetchall()

        db.close()

        if users:  # if users exist in group's table
            output_message = "USERNAME : NAME : MESSAGE\n\n"
            for user in users:
                output_message += f"🚩 {user[0]} : {user[1]} : {user[2]} : {user[3]} : {user[4]} : {user[5]}\n\n"
            await message.reply(output_message)
        else:
            await message.reply("⛔️ Ще нема звітів")


@dp.message_handler(commands="ban")
async def ban(message: types.Message):
    '''
    This header reads "/ban" string and after a space user id
    after that updates user's column "blacklisted" to 1 (user will be banned)
    '''

    if message.from_user.id in SUPER_USERS:  # if is admin
        info = user_input(message, "/ban").split(" ")
        if len(info) != 2:
            await message.reply("⛔️ Невірний формат!")
            return
        
        # select current group
        if info[0] == "self":
            ban_group = message.chat.id*-1
        else:
            ban_group   = int(info[0])

        # select yourself
        if info[1] == "self":
            user_to_ban = message.from_user.id
        else:
            user_to_ban = int(info[1])

        
        if not user_to_ban:
            await message.reply("⛔️ Можливо ти щось забув?")
        else:
            try:
                user_id  = user_to_ban
                group_id = ban_group
                db = sqlite3.connect(DB_NAME)

                # if group exists
                try:
                    db.execute(f"""
                        SELECT * FROM `{group_id}`
                    """)
                except sqlite3.OperationalError:
                    await message.reply("⛔️ Не існує такої групи!")
                    return

                user = db.execute(f"""
                    SELECT * FROM `{group_id}` WHERE user_id={user_id}
                """).fetchone()

                # if user exists
                if user:
                    db.execute(f"""
                        UPDATE `{group_id}` SET blacklisted=1 WHERE user_id={user_id}
                    """)
                    await message.answer("✅ Користувач отримав по своїй сідничці!")
                else:
                    await message.reply("⛔️ Користувач має бути зарегестрованим у грі!")

                db.commit()
                db.close()
                
            except ValueError:
                await message.reply("⛔️ Не знаю таких гравців")
    else:
        await message.reply("⛔️ Працює лишу в групах!")


@dp.message_handler(commands="ub")
async def unban(message: types.Message):
    '''
    This handler unban user by the argument (set blacklisted to 0)

    :user_id: user's id
    '''

    if message.from_user.id in SUPER_USERS:  # if is admin
        info = user_input(message, "/ub").split(" ")
        if len(info) != 2:
            await message.reply("⛔️ Невірний формат!")
            return

                # select current group
        if info[0] == "self":
            group_id = message.chat.id*-1
        else:
            group_id   = info[0]

        # select yourself
        if info[1] == "self":
            user_id = message.from_user.id
        else:
            user_id = info[1]

        if not user_id:
            await message.reply("⛔️ Ти забув уввести ID заблокованого користувача!")
        else:
            if user_id != "self" or group_id != "self":
                try:
                    t1,t2 = int(user_id), int(group_id)
                except ValueError:
                    await message.reply("⛔️ Невірний формат!")
                    db.close()
                    return

            db = sqlite3.connect(DB_NAME)
            db.execute("""
                UPDATE `{0}` SET blacklisted=0, spamcount=0 WHERE user_id={1}
            """.format(group_id, user_id))

            db.commit()
            db.close()

            await message.reply("✅ Користувач може повернутися до гри!")
    else:
        await message.reply("⛔️ Працює лише в групах!")


# REPORT "message"
@dp.message_handler(commands="r")
async def report(message: types.Message):
    '''
    This handler reads your message after "/r " and write it in the table `reports`

    :param report_message
    '''

    report_message = user_input(message, "/r")

    if len(report_message) < 10:
        if len(report_message.strip()) == 0:
            await message.reply("⛔️ Ти забув уввести свій звіт!")
        else:
            await message.reply("⛔️ Звіт дуже малий!")
    elif message.text[2] == "@":
        await message.reply("⛔️ Невірний формат!")
    elif "--" in message.text or "#" in message.text:
        await message.reply("⛔️ Невірний формат!")
    else:

        data = [message.chat.id * -1, message.chat.title,
                message.from_user.id, message.from_user.username,
                message.from_user.first_name, report_message]

        if data[0] < 0:
            data[0] *= -1 

        # if it's personal message then message.chat will be marked "Personal message"

        if data[1] is None:
            data[1] = "Личные сообщения"
        if data[3] is None:
            data[3] = "N/A"

        db = sqlite3.connect(DB_NAME)
        try:
            db.execute("""
                INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
        except sqlite3.OperationalError:
            db.execute("""
                CREATE TABLE `reports` (
                    group_id    INTEGER        NOT NULL,
                    group_name  VARCHAR(255)   NOT NULL,
                    user_id     INTEGER        NOT NULL,
                    username    VARCHAR(35)    NOT NULL,
                    name        VARCHAR(255)   NOT NULL,
                    message     TEXT           NOT NULL
                )
            """)
            db.execute("""
                INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            print("[+] Table `reports` didn't exist and was created!")
        db.commit()
        db.close()
        await message.reply("Дякуємо за звіт! 💛")

        print("[R] A report had sent!")


# CLEAR ALL REPORTS FROM TABLE `reports`
@dp.message_handler(commands="clear")
async def clear_reports(message: types.Message):
    '''
    This function delete all writes in the table `reports` by
    '''

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)
        data = db.execute("SELECT * FROM `reports`").fetchone()

        if data:
            db.execute("""
                DELETE FROM `reports`
            """)
            db.commit()
            db.close()

            await message.reply("✅ Звіти повністю очищені!")
        else:
            await message.reply("⛔️ Навіщо мені очищати пусту скриньку?")


# show statistics of playing user
@dp.message_handler(commands="statistic")
async def statistic(message: types.Message):
    '''
    This handler make and send an output message with user descending users by length
    '''

    if message.chat.type != "private":
        db = sqlite3.connect(DB_NAME)
        try:
            cursor = db.execute("""
                SELECT * FROM `{0}` ORDER BY length DESC
            """.format(message.chat.id * -1))
            users_data = cursor.fetchall()
        except sqlite3.OperationalError:
            await message.reply("⛔️ Нема гравців! Стань першим!")
            return
        finally:
            db.close()

        if not users_data:
            await message.reply("⛔️ Нема гравців! Стань першим!")
        else:
            output_message = "📊 Рейтинг гравців:\n\n"

            emojis = ["👑 ", "🥇 ", "🥈 ", "🥉 ", "😈 ", "😇"]
            i = 0

            for user_data in users_data:
                # (user_id, username, fisrtname, length, endtime, spamcount, blacklisted)
                user_data = ass_info_obj(user_data)

                if i < 6:
                    if user_data.blacklisted:
                        output_message += "💢"
                    else:
                        if i == 0:
                            if user_data.length == 0:
                                output_message += "     %s Безжопий царь %s\n\n" % (emojis[i], user_data.name)
                            else:
                                output_message += "     %s Царь %s — %d см\n\n" % (emojis[i], user_data.name, user_data.length)
                        else:
                            output_message += emojis[i]

                if user_data.blacklisted:
                    output_message += "{1} залишився без дупи через спам\n".format(i, user_data.name)
                else:
                    if not user_data.length:
                        if i != 0:
                            output_message += "{0}. {1} — не має сіднички\n".format(i, user_data.name, user_data.length)
                    else:
                        if i != 0:
                            output_message += "{0}. {1} — {2} см\n".format(i, user_data.name, user_data.length)
                    i += 1

            await message.reply(output_message)


# a user leaves the game
@dp.message_handler(commands="leave")
async def leave(message: types.Message):

    if message.chat.type != "private":  # if message was gotten in a group
        db = sqlite3.connect(DB_NAME)

        cursor = db.execute("""
        SELECT * FROM `{0}` WHERE user_id={1}
        """.format(message.chat.id * -1, message.from_user.id))

        ass_info = ass_info_obj(cursor.fetchone())

        if ass_info:  # if user isn't registered
            if ass_info.blacklisted:  # if user is blacklisted
                await message.reply("⛔️ Ні, дружок, таке не проканає 😏")
            else:  # if user isn't blacklisted
                db.execute("""
                    DELETE FROM `{0}` WHERE user_id={1}
                """.format(message.chat.id * -1, message.from_user.id))
                await message.reply("✅ Ти покинув гру! Шкода такий гарний зад.")
        else:  # if user isn't registered
            await message.reply("⛔️ Ти не зарегестрований у грі!")
        db.commit()
        db.close()
    else:  # if message was gotten from private message
        await message.answer("⛔️ Працює лише у групах!")


@dp.message_handler(commands="show")
async def show_users(message: types.Message):
    '''
    This function send message with all user from group via group id
    :group_id: Yeah, it's Group_id
    '''
    group_id = user_input(message, "/show")

    if message.from_user.id in SUPER_USERS:
        if group_id == "self":
            group_id = message.chat.id*-1
        if group_id:
            try:
                group_id = int(group_id)
                db = sqlite3.connect(DB_NAME)
                # (user_id, username, firstname, length, endtime, spamcount, blacklisted)
                try:
                    USERS = db.execute("SELECT * FROM `%d`" % group_id).fetchall()
                    output_message  = "👥 Group: <code>%s</code>\n" % group_id
                    output_message += "ID : USERNAME:NAME : SPAMCOUNT: IS_BANNED\n\n"

                    user_count = 0
                    for user in USERS:
                        user_count += 1
                        user = ass_info_obj(user)
                        if user.blacklisted == 1: # if blacklisted
                            blacklisted = "✅"
                        else:
                            blacklisted = "❌"
                        output_message += f"▶️ <code>{user.id}</code> : <b>{user.username}</b> : <b>{user.name}</b> : {user.spamcount} : {blacklisted}\n"
                    
                    if user_count == 1:
                        output_message += "\n📌 Totally: 1 user"                    
                    else:
                        output_message += f"\n📌 Totally: {user_count} users"

                    await message.reply(output_message, parse_mode="HTML")
                except sqlite3.OperationalError:
                    await message.reply("⛔️ Такої групи не існує")
                finally:
                    db.close()

            except ValueError:
                await message.reply("⛔️ Невірний формат!")
        else:
            await message.reply("⛔️ Ти забув про ідентифікатор групи!")


@dp.message_handler(commands="start")
async def start(message: types.Message):
    '''
    Send start message from variable 'content'
    '''

    await message.reply(content["start"])


@dp.message_handler(commands="about")
async def about(message: types.Message):
    '''
    Send about message from variable 'content'
    '''

    await message.reply(content["about"])


@dp.message_handler(commands="help")
async def user_help(message: types.Message):
    '''
    Send help message from variable 'content'
    '''

    await message.reply(content["help"])


@dp.message_handler(commands="admin")
async def admin(message: types.Message):
    '''
    Send admin message from variable 'content'
    '''

    if message.from_user.id in SUPER_USERS:
        await message.reply(content["admin"])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
