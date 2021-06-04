#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# TODO написать основной скрипт для функции "ass"
# TODO оформить базу данных
# TODO написать диалоги
# TODO написать нормально отчёты и сравнивание за временем

import config
import json
import random
import sqlite3
import os
import time

from aiogram import Bot, Dispatcher, executor, types

queries = {
    "create_table" : """
        CREATE TABLE `users`(
                id          INTEGER     PRIMARY KEY NOT NULL,
                username    TEXT                    NOT NULL,
                name        TEXT                    NOT NULL,
                length      INTEGER                 NOT NULL,
                endtime     INTEGER                 NOT NULL
            );
    """,
    "put_user" : """
        INSERT INTO `users`(id,username, name, length, endtime)
        VALUES (?,?,?,?,?)
    """
}

def ass_main(ass_info, db):
    tmp_length = random.randint(-10, 10)

    output_message = "@{0}, твоя жопка ".format(ass_info[1])

    if tmp_length == 0:
        # message with no profit
        output_message += "не сменила размера. "
    elif tmp_length > 0:
        # message with profit
        output_message += ("увеличилась на {0}! ".format(tmp_length))
    elif tmp_length < 0:
        # message with bad profit
        output_message += ("уменьшилась на {0}! ".format(tmp_length * -1))

    ass_info = list(ass_info)
    ass_info[3] = ass_info[3] + tmp_length

    if ass_info[3] < 0:
        ass_info[3] = 0
        output_message += "Зараз ти не маєш файного заду."
    else:
        output_message += "Текущий размер жопки: {0} см. ".format(ass_info[3])

    # write to database
    timeleft = random.randint(3600, 86400)
    end_time = int(time.time()) + timeleft

    last_time = end_time - int(time.time())

    if last_time < 0:
        minutes = ((last_time // 60) - (last_time // 3600) * 60) * -1
        hours = last_time // 3600 * -1
    else:
        minutes = (last_time // 60) - (last_time // 3600) * 60
        hours = last_time // 3600
    output_message += "Продолжай играть через {0} ч., {1} м.".format(hours, minutes)
    db.execute("""
            UPDATE `users` SET length={0}, endtime={2} WHERE id={1}
        """.format(ass_info[3], ass_info[0], end_time))

    return output_message

# database initialization

if "list" in os.listdir("."):
    print("[+] Database had already created!")
else:
    db = sqlite3.connect("list")
    db.execute(queries["create_table"])
    print("[+] Database is successfully created!")
    db.commit()
    db.close()

# initialization

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)

if config.DEBUG == True:
    print("[!] WARNING! DEBUG mode is on!")
    @dp.message_handler(commands=["ass","help"])
    async def ass(message: types.Message):
        await message.reply("ВКЛЮЧЕН РЕЖИМ ОТКЛАДКИ! БОТ НЕ РАБОТАЕТ!")

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)

# dialogs
content = json.loads( open("dialogs.json","r",encoding="utf8").read())
# ass script

@dp.message_handler(commands=["start"])
async def ass(message: types.Message):
    await message.reply(content["start"])

@dp.message_handler(commands=["ass"])
async def ass(message: types.Message):
    if not message.chat["id"] != "495137368" or config.DEBUG:
        await message.answer("Я працюю лише в деякій групі!")
    else:
        db = sqlite3.connect("list")
        # if user exists in database

        cursor = db.execute("""
        SELECT * FROM `users` WHERE id={0}
        """.format(message.from_user["id"]))
        ass_info = cursor.fetchone()

        if ass_info is None:
            userinfo = (message.from_user["id"], message.from_user["username"], message.from_user["first_name"], 0, 0)
            db.execute(queries["put_user"], userinfo)
            cursor = db.execute("""
            SELECT * FROM `users` WHERE id={0}
            """.format(message.from_user["id"]))
            ass_info = cursor.fetchone()
            await message.reply("@{0}, вітаю в нашій когорті, хлопче/дівчино".format(ass_info[1]))
            await message.reply(ass_main(ass_info, db))
        else:
            if int(time.time()) >= ass_info[4]:
                await message.reply(ass_main(ass_info, db))
            else:
                last_time = ass_info[4] - int(time.time())
                minutes = last_time // 60
                hours = last_time // 3600

                minutes -= hours * 60

                if hours == 0:
                    await message.reply(
                        "@{0}, ти вже грав! Зачекай {1} хв.".format(ass_info[1], minutes)
                    )
                else:
                    await message.reply(
                        "@{0}, ти вже грав! Зачекай {1} год., {2} хв.".format(ass_info[1], hours, minutes)
                    )

        db.commit()
        db.close()

# help
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.reply(content["help"])

@dp.message_handler(commands=["leave"])
async def leave(message: types.Message):
    db = sqlite3.connect("list")

    cursor = db.execute("""
    SELECT * FROM `users` WHERE id={0}
    """.format(message.from_user["id"]))
    ass_info = cursor.fetchone()
    if not ass_info:
        await message.reply("Ти не був зарегестрований у грі!")
    else:
        db.execute("""
            DELETE FROM `users` WHERE id={0}
        """.format(message.from_user["id"]))
        await message.reply("Ти покинув гру! Шкода такий гарний зад.")
    db.commit()
    db.close()


# menu
@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    buttons = [
        types.KeyboardButton(text="/ass"),
        types.KeyboardButton(text="/leave"),
        types.KeyboardButton(text="/help")
    ]

    keyboard.add(*buttons)
    await message.reply("Меню открыто: ",reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
