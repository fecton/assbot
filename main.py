#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import config
import json
import random
import sqlite3
import os
import time

from aiogram import Bot, Dispatcher, executor, types

if not config.TOKEN:
    print("[!] Invalid token!!")
    exit()


def ass_main(ass_info, database, group_id):
    ass_info = {
        "id": ass_info[0],
        "username": ass_info[1],
        "name": ass_info[2],
        "length": ass_info[3],
        "endtime": ass_info[4],
        "spamcount": ass_info[5],
        "blacklisted": ass_info[6]
    }

    if ass_info["endtime"] > int(time.time()):

        last_time = ass_info["endtime"] - int(time.time())
        hours = int(last_time / 3600)
        minutes = int((last_time / 60) - (hours * 60))

        if hours == 0:
            output_message = (
                "@{0}, ти вже грав! Зачекай {1} хв.".format(ass_info["username"], minutes)
            )
        else:
            if minutes == 0:
                output_message = (
                    "@{0}, ти вже грав! Зачекай {1} год.".format(ass_info["username"], hours)
                )
            else:
                output_message = (
                    "@{0}, ти вже грав! Зачекай {1} год., {2} хв.".format(ass_info["username"], hours, minutes)
                )

        database.execute("""
            UPDATE `{0}` SET spamcount={1} WHERE user_id={2}
        """.format(group_id, ass_info["spamcount"] + 1, ass_info["id"]))
    else:
        tmp_length = random.randint(-10, 15)
        output_message = "@{0}, твоя дупця ".format(ass_info["username"])

        if tmp_length == 0:
            output_message += "не змінила розміру. "
        elif tmp_length > 0:
            output_message += ("підросла на {0} см! Зараз твоя дупця прям бомбезна. ".format(tmp_length))
        elif tmp_length < 0:
            if not ass_info["length"] - tmp_length <= 0:
                output_message += ("зменшилась на {0} см! Зараз твоя дупця вже не файна. ".format(tmp_length * -1))

        ass_info["length"] = ass_info["length"] + tmp_length

        if ass_info["length"] < 0:
            ass_info["length"] = 0
            output_message += "Зараз ти не маєш заду. "
        else:
            output_message += "\nНаразі ваша дупенція становить: {0} см. ".format(ass_info["length"])

        end_time = int(time.time()) + random.randint(3600, 86400)

        last_time = end_time - int(time.time())

        if last_time >= 0:
            minutes = (last_time // 60) - (last_time // 3600) * 60
            hours = last_time // 3600
        else:
            minutes = ((last_time // 60) - (last_time // 3600) * 60) * -1
            hours = last_time // 3600 * -1

        output_message += "Продовжуй грати через {0} год., {1} хв.".format(hours, minutes)
        database.execute("""
                UPDATE `{0}` SET length={1}, endtime={2}, spamcount=0 WHERE user_id={3}
            """.format(group_id, ass_info["length"], end_time, ass_info["id"]))

    return output_message


if "list" not in os.listdir("."):
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
    database.commit()
    database.close()
else:
    print("[+] Everything is fine!")

# initialization

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)
print("[+] Bot initialization was successfully!")

# if you want to read from json-file
content = json.loads(open("messages.json", "r", encoding="utf8").read())


@dp.message_handler(commands=["ass"])
async def ass(message: types.Message):
    if message.chat["type"] == "private":
        await message.answer("Я працюю лише в группах!")
    else:
        database = sqlite3.connect("list")

        group_id = message.chat["id"]*-1
        user_id = message.from_user["id"]
        username = message.from_user["username"]
        first_name = message.from_user["first_name"]

        try:
            database.execute("SELECT * FROM `%d`" % group_id)
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

            database.commit()
            print("[+] Table with name '%d' (%s) created successfully!" % (group_id, message.chat["title"]))

        # if user exists in database

        cursor = database.execute("""
        SELECT * FROM `{0}` WHERE user_id={1}
        """.format(group_id, user_id))
        ass_info = cursor.fetchone()

        if ass_info is None:
            userinfo = (user_id, username, first_name, 0, 0, 0, 0)
            database.execute("""
                INSERT INTO `%d`(user_id, username, name, length, endtime, spamcount, blacklisted)
                VALUES (?,?,?,?,?,?,?)
            """ % group_id, userinfo)

            cursor = database.execute("""
            SELECT * FROM `{0}` WHERE user_id={1}
            """.format(group_id, user_id))
            ass_info = cursor.fetchone()
            await message.reply(f"@{ass_info[1]}, вітаю в нашій когорті, хлопче/дівчино")
            await message.reply(ass_main(ass_info, database, group_id))
        else:
            if int(time.time()) >= ass_info[4]:
                await message.reply(ass_main(ass_info, database, group_id))
            else:
                if ass_info[6]:
                    await message.reply("%s, дружок, ти вже награвся, шуруй звідси." % first_name)
                else:
                    if ass_info[5] == 6:
                        database.execute("""
                            UPDATE `{0}` SET blacklisted=1, length=0 WHERE user_id={1}
                        """.format(group_id, user_id))
                        await message.reply("%s, я тобі попку збільшую, а ти мені спамиш. Мені взагалі-то теж не солодко постійно вам попу міряти. Все, дружок, тепер ти мене не будеш зайобувати — ти в муті." % first_name)
                    else:
                        await message.reply(ass_main(ass_info, database, group_id))

        database.commit()
        database.close()


@dp.message_handler(lambda message: message.text[:3] == "/bl")
async def ass(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        group_id = message.text[4:]

        if group_id == "":
            await message.reply("Ти забув ввести ID группи!")
        elif len(group_id) < 5:
            await message.reply("Неповний ID группи!")
        else:
            database = sqlite3.connect("list")
            cursor = database.execute("""
                SELECT * FROM `%s` WHERE blacklisted=1
            """ % group_id)
            users_data = cursor.fetchall()
            database.close()

            if not users_data:
                await message.reply("Нема заблокованих користувачів!")
            else:
                output_message = "ID : USERNAME : NAME\n\n"

                for user_data in users_data:
                    output_message += f"{user_data[0]} :  user_data[1] : user_data[2]\n"

                await message.reply(output_message)


@dp.message_handler(lambda message: message.text[:3] == "/ub")
async def unban(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        if message.chat["type"] == "private":
            await message.answer("Працює лишу у групах!")
        else:
            if not message.text[4:]:
                await message.reply("Ти забув уввести ID заблокованого користувача!")
            else:
                database = sqlite3.connect("list")
                database.execute("""
                    UPDATE `{0}` SET blacklisted=0, spamcount=0 WHERE user_id={1}
                """.format(message.chat["id"]*-1, message.text[4:]))

                database.commit()
                database.close()

                await message.reply("Користувач {0} може повернутися до гри!".format(id))


@dp.message_handler(lambda message: message.text[:2] == "/r")
async def report(message: types.Message):
    if len(message.text[3:]) < 10:
        if len(message.text[3:].strip()) == 0:
            await message.reply("Ти забув уввести свій звіт!")
        else:
            await message.reply("Звіт дуже малий!")
    elif message.text[2] == "@":
        await message.reply("Невірний формат!")
    else:
        data = (message.chat["id"]*-1, message.chat["title"],
                message.from_user["id"], message.from_user["username"],
                message.from_user["first_name"], message.text[3:])
        database = sqlite3.connect("list")
        database.execute("""
            INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        database.commit()
        database.close()
        await message.reply("Дякуємо за звіт! 💛")
        print("[R] A report had sent!")


@dp.message_handler(commands=["show_reports"])
async def show_reports(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        database = sqlite3.connect("list")
        cursor = database.execute("""
            SELECT * FROM `reports`
        """)

        reports = cursor.fetchall()

        if reports:
            output_message = "GROUP_ID : USER_ID : USERNAME : NAME : MESSAGE\n\n"
            for report in reports:
                output_message += "⛔️{0} : {1} : {2} : {3}\n      {3}\n\n".format(*report)

            database.close()

            await message.reply(output_message)
        else:
            await message.reply("Ще нема звітів!")


@dp.message_handler(commands=["clear_reports"])
async def clear_reports(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        database = sqlite3.connect("list")
        database.execute("""
            DELETE FROM `reports`
        """)
        database.commit()
        database.close()

        await message.reply("Звіти повністю очищені!")


@dp.message_handler(commands=["statistic"])
async def statistic(message: types.Message):
    if "private" == message.chat["type"]:
        await message.answer("Працює лише у групах!")
    else:
        database = sqlite3.connect("list")
        try:
            cursor = database.execute("""
                SELECT * FROM `{0}` ORDER BY length DESC
            """.format(message.chat["id"]*-1))
            users_data = cursor.fetchall()
        except sqlite3.OperationalError:
            await message.reply("Нема гравців! Стань першим!")
            return
        finally:
            database.close()

        if not users_data:
            await message.reply("Нема гравців! Стань першим!")
        else:
            i = 1
            output_message = "Рейтинг гравців:\n\n"

            emojis = ["👑 ", "🥇 ", "🥈 ", "🥉 ", "😈 ", "😇"]

            for user_data in users_data:
                try:
                    output_message += emojis[i-1]
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


@dp.message_handler(commands=["leave"])
async def leave(message: types.Message):
    if message.chat["type"] != "private":
        database = sqlite3.connect("list")

        cursor = database.execute("""
        SELECT * FROM `{0}` WHERE user_id={1}
        """.format(message.chat["id"]*-1, message.from_user["id"]))

        ass_info = cursor.fetchone()
        if ass_info:
            if not ass_info[6]:
                database.execute("""
                    DELETE FROM `{0}` WHERE user_id={1}
                """.format(message.chat["id"]*-1, message.from_user["id"]))
                await message.reply("Ти покинув гру! Шкода такий гарний зад.")
            else:
                await message.reply("Ні, таке не проканає 😏")
        else:
            await message.reply("Ти не зарегестрований у грі!")
        database.commit()
        database.close()
    else:
        await message.answer("Працює лише у групах!")


@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(
        types.KeyboardButton(text="/ass"),
        types.KeyboardButton(text="/leave"),
    )

    keyboard.row(
        types.KeyboardButton(text="/help"),
        types.KeyboardButton(text="/statistic")
    )

    await message.reply("Звичайно, друже: ", reply_markup=keyboard)


@dp.message_handler(commands=["start"])
async def ass(message: types.Message):
    await message.reply(content["start"])


@dp.message_handler(commands=["about"])
async def menu(message: types.Message):
    await message.reply(content["about"])


@dp.message_handler(commands=["help"])
async def user_help(message: types.Message):
    await message.reply(content["help"])


@dp.message_handler(commands=["admin_help"])
async def menu(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        await message.reply(content["admin_help"])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
