from aiogram import Bot, Dispatcher, types
from utils.db_core import DbCore
from data.config import TOKEN, DB_NAME
from os import path

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
db = DbCore()

if not path.exists(DB_NAME):

    # it created database if it doesn't exist + create tables

    print("[+] First start!")

    db.create_reports_table()
    print("[+] Report table was created successfully!")

    db.create_groups_name_table()
    print("[+] Group's name table was created successfully!")

else:
    print("[+] Everything is fine!")
