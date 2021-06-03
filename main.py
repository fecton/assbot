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

queries = {
    "create_table" : """
        CREATE TABLE `users`(
                id          INTEGER     PRIMARY KEY NOT NULL,
                username    TEXT                    NOT NULL,
                name        TEXT                    NOT NULL,
                length      INTEGER                 NOT NULL,
                starttime   INTEGER                 NOT NULL,
                endtime     INTEGER                 NOT NULL
            );
    """,
    "put_user" : """
        INSERT INTO `users`(id,username, name, length, starttime, endtime)
        VALUES (?,?,?,?,?,?)
    """
}


from aiogram import Bot, Dispatcher, executor, types

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
        await message.answer("ВКЛЮЧЕН РЕЖИМ ОТКЛАДКИ! БОТ НЕ РАБОТАЕТ!")

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)

# dialogs
content = json.loads( open("dialogs.json","r",encoding="utf8").read())
# ass script
@dp.message_handler(commands=["ass"])
async def ass(message: types.Message):
    if message.chat["id"] == "495137368":
        await message.answer("Бот работает только в одной группе!")
    else:
        db = sqlite3.connect("list")
        # if user exists in database

        cursor = db.execute("""
        SELECT * FROM `users` WHERE id={0}
        """.format(message.from_user["id"]))
        ass_info = cursor.fetchone()
        await message.answer(ass_info)
        if ass_info is None:
            userinfo = (message.from_user["id"], message.from_user["username"], message.from_user["first_name"], 0, 1, 0)
            db.execute(queries["put_user"], userinfo)
            await message.answer("joined")
        else:
            # ass script
            if ass_info[4] >= ass_info[5]:

                tmp_length = random.randint(-10, 15)

                if tmp_length == 0:
                    # message with no profit
                    await message.answer("Размер не поменялся")
                elif tmp_length > 0:
                    # message with profit
                    await message.answer("Увеличилась на {0}".format(tmp_length))
                elif tmp_length < 0:
                    # message with bad profit
                    await message.answer("Уменьшилась на {0}!".format(tmp_length * -1))

                ass_info = list(ass_info)
                ass_info[3] = ass_info[3]+tmp_length

                if ass_info[3] < 0:
                    ass_info[3] = 0

                await message.answer("Текущий размер: {0}".format(ass_info[3]))

                # write to database

                timeleft = random.randint(3600, 86400)

                start_time = int(time.time())
                end_time = time.time() + timeleft

                db.execute("""
                    UPDATE `users` SET length={0}, starttime={1}, endtime={2} WHERE id={1}
                """.format(ass_info[3], ass_info[0], start_time, end_time))
            else:
                last_time = int(time.time()) - ass_info[5]
                print(time.localtime(last_time))
                # await message.answer("Waiting time didn't end, please wait {0} hours and {1} minutes".format())

        db.commit()
        db.close()
        # await message.answer("[+] Operation is completed!")

# help
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(content["help"])

@dp.message_handler(commands=["leave"])
async def leave(message: types.Message):
    db = sqlite3.connect("list")
    db.execute("""
        DELETE FROM `users` WHERE id={0}
    """.format(message.from_user["id"]))
    db.commit()
    db.close()
    await message.reply("Вы вышли из игры! Данные о вашей жопке удалены!")

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






