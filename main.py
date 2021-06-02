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

from aiogram import Bot, Dispatcher, executor, types

# database initialization

if "list" in os.listdir("."):
    print("[+] Database had already created!")
else:
    db = sqlite3.connect("list")
    db.execute("""
        CREATE TABLE `users`(
                username    TEXT        PRIMARY KEY NOT NULL,
                name        TEXT        NOT NULL,
                length      INTEGER     NOT NULL );
    """)
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
@dp.message_handler(commamds=["ass"])
async def ass(message: types.Message):

    await message.answer(content["help"])
# help
@dp.message_handler(commamds=["help"])
async def help(message: types.Message):
    await message.answer(content["help"])
# menu
@dp.message_handler(commamds=["menu"])
async def menu(message: types.Message):
    await message.answer("Тут должно быть меню")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)






