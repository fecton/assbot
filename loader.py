from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils import DbCore
from config import TOKEN, DB_NAME, logger

from os import path

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DbCore()

if not path.exists(DB_NAME):
    logger.info('First start!')

    db.create_reports_table()
    logger.debug("Report table was created successfully!")

    db.create_groups_name_table()
    logger.debug("Group's name table was created successfully!")

else:
    logger.debug("The database exists and works properly!")
