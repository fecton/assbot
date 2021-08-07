import sqlite3
from aiogram import Bot, Dispatcher, types

from data.config import TOKEN, DB_NAME
from os import path

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


if not path.exists(DB_NAME):
    from database.create import CREATE_table_groups_name, CREATE_table_reports
    # it created database if it doesn't exist + create tables
    db = sqlite3.connect(DB_NAME)
    print("[+] First start!")

    db.execute(CREATE_table_reports)
    print("[+] Report table was created successfully!")

    db.execute(CREATE_table_groups_name)
    print("[+] Group's name table was created successfully!")

    db.commit()
    db.close()

else:
    print("[+] Everything is fine!")
