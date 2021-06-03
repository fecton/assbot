#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# TODO написать основной скрипт для функции "ass"
# TODO оформить базу данных
# TODO сделать чтение и сравнивание данных из базы данных
# TODO фиксиить ошибки
# TODO написать диалоги

import config
import json
import random
import sqlite3
import os

queries = {
    "create_table" : """
        CREATE TABLE `users`(
                id          INTEGER     PRIMARY KEY NOT NULL,
                username    TEXT                    NOT NULL,
                name        TEXT                    NOT NULL,
                length      INTEGER                 NOT NULL,
                timeleft    INTEGER                 NOT NULL
            );
    """,
    "put_user" : """
        INSERT INTO `users`(id,username, name, length, timeleft)
        VALUES (?,?,?,?,?)
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
        await message.answer("Бот не работает только в одной группе!")
    else:
        db = sqlite3.connect("list")
        # if user exists in database

        cursor = db.execute("""
                SELECT * FROM `users` WHERE id={0}
        """.format(message.from_user["id"]))

        ass_info = cursor.fetchall()[0]
        if ass_info == []:
            userinfo = (message.from_user["id"], message.from_user["username"], message.from_user["first_name"], 0, 0)
            db.execute(queries["put_user"], userinfo)
            await message.answer("joined")
        else:
            # ass script
            tmp_length = random.randint(-10,15)

            if tmp_length == 0:
                # message with no profit
                pass
            elif tmp_length > 0:
                # message with profit
                pass
            elif tmp_length < 0:
                # message with bad profit
                pass
            # ass_info[3]
            ass_info = list(ass_info)
            ass_info[3] = ass_info[3]+tmp_length
            userinfo = tuple(ass_info)

            await message.answer(userinfo)

        db.commit()
        db.close()
        await message.answer("complete")

# help
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(content["help"])

# menu
@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    await message.answer("Тут должно быть меню")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)






