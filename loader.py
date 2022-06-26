import logging.config

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.db_core import DbCore
from data.config import TOKEN, DB_NAME
from data.logger_config import LOGGING_CONFIG

from os import path

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('assbot_logger')

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
db = DbCore()

if not path.exists(DB_NAME):
    # it created database if it doesn't exist + create tables

    logger.info('First start!')

    db.create_reports_table()
    logger.info("Report table was created successfully!")

    db.create_groups_name_table()
    logger.info("Group's name table was created successfully!")

else:
    logger.info("Everything is fine!")
