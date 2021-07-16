#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__version__ = '1.3'

import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from random  import randint
from json    import loads
from time    import time
from os      import path

from config import *

if not TOKEN:
    print("[!] Empty token!!")
    exit()

# initialization
bot = Bot(TOKEN)
dp = Dispatcher(bot)
print("[+] Bot initialization was successfully!")

# if you want to read from json-file
content = loads(open("messages.json", "r", encoding="utf8").read())


class ass_info_obj():
    '''
    Used for better understanding ass_info
    '''
    def __init__(self, ass_info: tuple):
        self.id          = ass_info[0]
        self.username    = ass_info[1]
        self.name        = ass_info[2]
        self.length      = ass_info[3]
        self.endtime     = ass_info[4]
        self.spamcount   = ass_info[5]
        self.blacklisted = ass_info[6]


def ass_main(ass_info, database, group_id):
    '''
    This function is backend part of function `ass`

    :param ass_info: Information about user from a database
    :param database: Yeah, it's a database
    :param group_id: Yeah, that's a group id
    :return:         Send to a database an query which change data.
    '''

    ass_info = ass_info_obj(ass_info)

    if ass_info.endtime > int(time()):
        last_time = ass_info.endtime - int(time())

        hours = int(last_time / 3600)
        last_time -= hours * 3600

        minutes = int(last_time / 60)
        last_time -= minutes * 60

        if ass_info.username == ass_info.name:
            ass_info.username = ass_info.name
        else:
            try:
                ass_info.username = "@" + ass_info.username
            except TypeError:
                ass_info.username = "Анонимус"

        if hours == 0:
            if minutes == 0:
                output_message = (
                    "{0}, готуйсь заглянути залишилося менше хвилини".format(ass_info.username, minutes)
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

        database.execute("""
            UPDATE `{0}` SET spamcount={1} WHERE user_id={2}
        """.format(group_id, ass_info.spamcount + 1, ass_info.id))
    else:
        tmp_length = randint(-8, 15)

        if ass_info.username == ass_info.name:
            ass_info.username = ass_info.name
        else:
            try:
                ass_info.username = "@" + ass_info.username
            except TypeError:
                ass_info.username = "Анонимус"

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
        database.execute("""
                UPDATE `{0}` SET length={1}, endtime={2}, spamcount=0 WHERE user_id={3}
            """.format(group_id, ass_info.length, end_time, ass_info.id))

    return output_message


if not path.exists("list"):
    # it created database if it doesn't exist + create tables
    database = sqlite3.connect("list")
    database.execute("""
        CREATE TABLE `reports` (
            group_id    INTEGER        NOT NULL,
            group_name  VARCHAR(255)   NOT NULL,
            user_id     INTEGER        NOT NULL,
            username    VARCHAR(35)    NOT NULL,
            name        VARCHAR(255)   NOT NULL,
            message     TEXT           NOT NULL
        )
    """)
    print("[+] Report table is created successfully!")
    database.execute("""
        CREATE TABLE `groups_name` (
            group_id    INTEGER      NOT NULL,
            group_name  VARCHAR(255) NOT NULL
        )
    """)
    print("[+] Groups_name  table is created successfully!")
    database.commit()
    database.close()
else:
    print("[+] Everything is fine!")


@dp.message_handler(commands=["ass"])
async def ass(message: types.Message):
    '''
    This function is frontend and it takes (group_id, user_id, username, first_name)
    for a database's row. That's a main script for playing: it's generates random number and influence
    on length, counts spam count and send to ban bad users.
    '''

    if message.from_user.is_bot:  # ignore bots
        return

    if message.chat.type == "private":  # if write /ass in private messages
        await message.answer("Я працюю лише в группах!")
    else:  # working in a group

        group_id = message.chat.id * -1
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name

        database = sqlite3.connect("list")

        try:  # if group's table exists
            cursor = database.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            ass_info = cursor.fetchone()
        except sqlite3.OperationalError:
            # creating table with name by group_id

            database.execute("""
            CREATE TABLE `%d`(
                    user_id     INTEGER     PRIMARY KEY NOT NULL,
                    username    VARCHAR(35)             NOT NULL,
                    name        VARCHAR(255)            NOT NULL,
                    length      INTEGER                 NOT NULL,
                    endtime     INTEGER                 NOT NULL,
                    spamcount   INTEGER                 NOT NULL,
                    blacklisted BOOLEAN                 NOT NULL
                );""" % group_id)

            print("[+] Table with name '%d' (%s) created successfully!" % (group_id, message.chat.title))

            cursor = database.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            ass_info = cursor.fetchone()

            try:

                database.execute("""
                    INSERT INTO `groups_name` (group_id, group_name)
                    VALUES (?,?)
                """, (group_id, message.chat.title))

            except sqlite3.OperationalError:

                database.execute("""
                    CREATE TABLE `groups_name` (
                        group_id    INTEGER      NOT NULL,
                        group_name  VARCHAR(255) NOT NULL
                    )
                """)
                database.execute("""
                    INSERT INTO `groups_name` (group_id, group_name)
                    VALUES (?,?)
                """, (group_id, message.chat.title))

                print("[+] Table `groups_name` created and row was added successfully!")

        database.commit()

        # if user exists in database

        if ass_info is None:  # if user didn't be registered in the game
            if username is None:  # if user doesn't have username
                username = first_name
            userinfo = (user_id, username, first_name, 0, 0, 0, 0)
            database.execute("""
                INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted)
                VALUES (?,?,?,?,?,?,?)
            """ % group_id, userinfo)

            cursor = database.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            ass_info = cursor.fetchone()

            if ass_info[1] == ass_info[2]:  # if user doesn't have username only firstname
                await message.reply(f"{ass_info[1]}, вітаю в нашій когорті, хлопче/дівчино")
            else:  # if user has username
                await message.reply(f"@{ass_info[1]}, вітаю в нашій когорті, хлопче/дівчино")

            await message.reply(ass_main(ass_info, database, group_id))
        else:
            if ass_info[6]:  # if already blacklisted
                await message.reply("%s, дружок, ти вже награвся, шуруй звідси." % first_name)
            else:  # if not blacklisted
                if int(time()) >= ass_info[4]:  # if last_time already pasted
                    await message.reply(ass_main(ass_info, database, group_id))
                else:
                    if ass_info[5] == 8:  # if spamcount == 8 -> blacklisted
                        database.execute("""
                            UPDATE `{0}` SET blacklisted=1, length=0 WHERE user_id={1}
                        """.format(group_id, user_id))
                        await message.reply(
                            "%s, я тобі попку збільшую, а ти мені спамиш. Мені взагалі-то теж не солодко постійно вам попу міряти. Все, дружок, тепер ти мене не будеш зайобувати — ти в муті."
                            % first_name
                        )
                    else:
                        await message.reply(ass_main(ass_info, database, group_id))

        database.commit()
        database.close()


@dp.message_handler(lambda message: message.text[:3] == "/bl")
async def show_blacklisted_users(message: types.Message):
    '''
    This function shows all banned users in a group
    /bl :user_id:   Group ID
    '''

    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:  # if is admin
        group_id = message.text[4:]

        if group_id == "":
            await message.reply("Ти забув ввести ID группи!")
        elif len(group_id) < 5:
            await message.reply("Неповний ID группи!")
        else:
            try:
                group_id_tmp = int(group_id)
            except ValueError:
                await message.reply("Вибач, але не знаю такої групи.")
                return

            database = sqlite3.connect("list")
            try:
                cursor = database.execute("""
                    SELECT * FROM `{0}` WHERE blacklisted=1
                """.format(group_id))
                users_data = cursor.fetchall()
            except sqlite3.OperationalError:
                await message.reply("Вибач, але не знаю такої групи.")
                database.close()
                return
            finally:
                database.close()

            if not users_data:
                await message.reply("Нема заблокованих користувачів!")
            else:
                output_message = "ID : USERNAME : NAME\n\n"

                for user_data in users_data:
                    if user_data[1] == user_data[2]:
                        output_message += f"{user_data[0]} :  {user_data[1]}\n"
                    else:
                        output_message += f"{user_data[0]} :  @{user_data[1]} : {user_data[2]}\n"

                await message.reply(output_message)


@dp.message_handler(commands=["show_groups"])
async def show_groups(message: types.Message):
    '''
    This function shows all registered in the game groups (its id and its name)
    '''

    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:
        database = sqlite3.connect("list")

        # cursorObj = database.cursor()
        # cursorObj.execute("SELECT name FROM sqlite_master WHERE type='table'")
        try:
            groups_info = database.cursor().execute("SELECT * FROM `groups_name`").fetchall()
        except sqlite3.OperationalError:
            print("[!] The table `groups_name` doesn't exist or was deleted, created new one")
            database.execute("""
                CREATE TABLE `groups_name` (
                    group_id    INTEGER      NOT NULL,
                    group_name  VARCHAR(255) NOT NULL
                )
            """)

            database.execute("""
                INSERT INTO `groups_name` (group_id, group_name)
                VALUES (?,?)
            """, (message.chat.id *-1, message.chat.title)
            )
            groups_info = database.cursor().execute("SELECT * FROM `groups_name`").fetchall()

        database.close()

        groups_dict = dict()

        for group in groups_info:
            groups_dict[group[0]] = group[1]

        # table_list = [x[0] for x in cursorObj.fetchall() if x[0] not in ["reports","groups_name"]]

        output_message = "💁<i><b>TABLES</b></i>\n"+"="*16+"\n"
        for key in groups_dict.keys():
            output_message += str(key) + " : " + groups_dict[key] + "\n"

        await message.reply(output_message, parse_mode="HTML")


# SHOW REPORTS FROM TABLE `reports`
@dp.message_handler(commands=["show_reports"])
async def show_reports(message: types.Message):
    '''
    This function show all rows from table `reports` and send it in one message
    '''

    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:
        database = sqlite3.connect("list")

        cursor = database.execute("SELECT * FROM `reports`")
        users = cursor.fetchall()
        if users:  # if users exist in group's table
            output_message = "USER_ID : USERNAME : NAME : MESSAGE\n"
            for user in users:
                output_message += f"🟥 {user[2]} : {user[3]} : {user[4]} : {user[5]}\n"
            await message.reply(output_message)
        else:
            await message.reply("Ще нема звітів")
        database.close()


@dp.message_handler(lambda message: message.text[:4] == "/ban")
async def ban(message: types.Message):
    '''
    This header reads "/ban" string and after a space user id
    after that updates user's column "blacklisted" to 1 (user will be banned)

    :param message.text[5:]: user id
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:  # if is admin
        if message.chat.type == "private":
            await message.answer("Працює лишу у групах!")
        else:
            if not message.text[5:]:
                await message.reply("Можливо ти щось забув?")
            else:
                try:
                    user_id = int(message.text[5:])
                    group_id = message.chat.id * -1
                    database = sqlite3.connect("list")

                    # if user exists

                    user = database.execute(f"""
                        SELECT * FROM `{group_id}` WHERE user_id={user_id}
                    """).fetchone()

                    if user:
                        database.execute(f"""
                            UPDATE `{group_id}` SET blacklisted=1 WHERE user_id={user_id}
                        """)
                    else:
                        database.execute(f"""
                            INSERT INTO `{group_id}` (user_id,username,name,length,endtime,spamcount,blacklisted)
                            VALUES (?,?,?,?,?,?,?)
                        """, (user_id, message.from_user.username, message.from_user.first_name, 0, 0, 0, 1)
                                         )

                    database.commit()
                    database.close()
                    await message.answer("Користувач отримав по своїй сідничці!")
                except ValueError:
                    await message.reply("Не знаю таких гравців.")


@dp.message_handler(lambda message: message.text[:3] == "/ub")
async def unban(message: types.Message):
    '''
    This handler unban user by the argument (set blacklisted to 0)

    :user_id: user's id
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:  # if is admin
        if message.chat.type == "private":
            await message.answer("Працює лишу у групах!")
        else:
            user_id = message.text[4:]
            if not user_id:
                await message.reply("Ти забув уввести ID заблокованого користувача!")
            else:
                try:
                    tmp = int(user_id)
                except ValueError:
                    await message.reply("Невірний формат!")
                    return

                database = sqlite3.connect("list")
                database.execute("""
                    UPDATE `{0}` SET blacklisted=0, spamcount=0 WHERE user_id={1}
                """.format(message.chat.id * -1, user_id))

                database.commit()
                database.close()

                await message.reply("Користувач може повернутися до гри!")


# REPORT "message"
@dp.message_handler(lambda message: message.text[:2] == "/r")
async def report(message: types.Message):
    '''
    This handler reads your message after "/r " and write it in the table `reports`

    :param message.text[3:]
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if len(message.text[3:]) < 10:
        if len(message.text[3:].strip()) == 0:
            await message.reply("Ти забув уввести свій звіт!")
        else:
            await message.reply("Звіт дуже малий!")
    elif message.text[2] == "@":
        await message.reply("Невірний формат!")
    elif "--" in message.text or "#" in message.text:
        await message.reply("Невірний формат!")
    else:

        data = [message.chat.id * -1, message.chat.title,
                message.from_user.id, message.from_user.username,
                message.from_user.first_name, message.text[3:]]

        # if it's personal message then message.chat will be marked "Personal message"
        if data[1] is None:
            data[1] = "Личные сообщения"

        database = sqlite3.connect("list")
        try:
            database.execute("""
                INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
        except sqlite3.OperationalError:
            database.execute("""
                CREATE TABLE `reports` (
                    group_id    INTEGER        NOT NULL,
                    group_name  VARCHAR(255)   NOT NULL,
                    user_id     INTEGER        NOT NULL,
                    username    VARCHAR(35)    NOT NULL,
                    name        VARCHAR(255)   NOT NULL,
                    message     TEXT           NOT NULL
                )
            """)
            database.execute("""
                INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            print("[+] Table `reports` didn't exist and was created!")
        database.commit()
        database.close()
        await message.reply("Дякуємо за звіт! 💛")
        print("[R] A report had sent!")


# CLEAR ALL REPORTS FROM TABLE `reports`
@dp.message_handler(commands=["clear_reports"])
async def clear_reports(message: types.Message):
    '''
    This function delete all writes in the table `reports` by
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:
        database = sqlite3.connect("list")
        database.execute("""
            DELETE FROM `reports`
        """)
        database.commit()
        database.close()

        await message.reply("Звіти повністю очищені!")


# show statistics of playing user
@dp.message_handler(commands=["statistic"])
async def statistic(message: types.Message):
    '''
    This handler make and send an output message with user descending users by length
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if message.chat.type == "private":
        await message.answer("Працює лише у групах!")
    else:
        database = sqlite3.connect("list")
        try:
            cursor = database.execute("""
                SELECT * FROM `{0}` ORDER BY length DESC
            """.format(message.chat.id * -1))
            users_data = cursor.fetchall()
        except sqlite3.OperationalError:
            await message.reply("Нема гравців! Стань першим!")
            return
        finally:
            database.close()

        if not users_data:
            await message.reply("Нема гравців! Стань першим!")
        else:
            output_message = "Рейтинг гравців:\n\n"

            emojis = ["👑 ", "🥇 ", "🥈 ", "🥉 ", "😈 ", "😇"]
            i = 1
            for user_data in users_data:
                try:
                    if user_data[6]:
                        output_message += "💢"
                    else:
                        output_message += emojis[i - 1]
                except IndexError:
                    pass

                if user_data[6]:
                    output_message += "{0}. {1} залишився без дупи через спам\n".format(i, user_data[2])
                else:
                    if not user_data[3]:
                        output_message += "{0}. {1} — не має сіднички\n".format(i, user_data[2], user_data[3])
                    else:
                        output_message += "{0}. {1} — {2} см\n".format(i, user_data[2], user_data[3])
                    i += 1

            await message.reply(output_message)


# a user leaves the game
@dp.message_handler(commands=["leave"])
async def leave(message: types.Message):
    if message.from_user.is_bot:  # ignore bots
        return

    if message.chat.type != "private":  # if message was gotten in a group
        database = sqlite3.connect("list")

        cursor = database.execute("""
        SELECT * FROM `{0}` WHERE user_id={1}
        """.format(message.chat.id * -1, message.from_user.id))

        ass_info = cursor.fetchone()
        if ass_info:  # if user isn't registered
            if ass_info[6]:  # if user is blacklisted
                await message.reply("Ні, таке не проканає 😏")
            else:  # if user isn't blacklisted
                database.execute("""
                    DELETE FROM `{0}` WHERE user_id={1}
                """.format(message.chat.id * -1, message.from_user.id))
                await message.reply("Ти покинув гру! Шкода такий гарний зад.")
        else:  # if user isn't registered
            await message.reply("Ти не зарегестрований у грі!")
        database.commit()
        database.close()
    else:  # if message was gotten from private message
        await message.answer("Працює лише у групах!")


@dp.message_handler(lambda message: message.text[:5] == "/show")
async def show_users(message: types.Message):
    '''
    This function send message with all user from group via group id
    :group_id: Yeah, it's Group_id
    '''
    group_id = message.text[6:].strip(" ")

    if message.from_user.id in SUPER_USERS:
        if group_id:
            try:
                group_id = int(group_id)
                database = sqlite3.connect("list")

                try:
                    USERS = database.execute(f"SELECT * FROM `{group_id}`").fetchall()
                    output_message = "ID : USERNAME : NAME : SPAMCOUNT: IS_BANNED\n"
                    for user in USERS:
                        if user[6] == 1:
                            output_message += f"{user[0]} : {user[1]} : {user[2]} : {user[5]} : True\n"
                        else:
                            output_message += f"{user[0]} : {user[1]} : {user[2]} : {user[5]} : False\n"

                    await message.reply(output_message)
                except sqlite3.OperationalError:
                    await message.reply("Такої групи не існує")
                finally:
                    database.close()
                    return

                database.close()
            except ValueError:
                await message.reply("Невірний формат!")
        else:
            await message.reply("Ти забув про ідентифікатор групи!")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    '''
    Send start message from variable 'content'
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    await message.reply(content["start"])


@dp.message_handler(commands=["about"])
async def about(message: types.Message):
    '''
    Send about message from variable 'content'
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    await message.reply(content["about"])


@dp.message_handler(commands=["help"])
async def user_help(message: types.Message):
    '''
    Send help message from variable 'content'
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    await message.reply(content["help"])


@dp.message_handler(commands=["admin_help"])
async def admin_help(message: types.Message):
    '''
    Send admin_help message from variable 'content'
    '''
    if message.from_user.is_bot:  # ignore bots
        return

    if message.from_user.id in SUPER_USERS:
        await message.reply(content["admin_help"])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
