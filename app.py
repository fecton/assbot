#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Open-Source AssBot 2022
# ------------------------------
#
# Made with love by Fecton
# https://www.github.com/fecton
#
# ------------------------------
# Enjoy using! ^_^

from aiogram import Dispatcher, executor

import middlewares
from data.logger_config import LOGGING_CONFIG
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from handlers import dp
from loader import logger

__version__ = "1.6.0"

async def on_startup(dp: Dispatcher):
    middlewares.setup(dp)
    logger.debug('Setting up default commands...')
    await set_default_commands(dp)
    logger.debug('Notifying admins on start up...')
    await on_startup_notify(dp)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
