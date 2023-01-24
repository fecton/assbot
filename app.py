#!/usr/bin python3
# -*- encoding: utf-8 -*-

# Open-Source AssBot 2023
# ------------------------------
#
# Made with love by Fecton
# alytvynenko.online
# github.com/fecton
#
# ------------------------------
# Enjoy using! ^_^

from aiogram import Dispatcher, executor

import middlewares
import os
from utils.start_setup import on_startup_notify, set_default_commands
from handlers import dp
from loader import logger

async def on_startup(dp: Dispatcher):
    middlewares.setup(dp)
    logger.debug('Setting up default commands...')
    await set_default_commands(dp)
    logger.debug('Notifying admins on start up...')
    await on_startup_notify(dp)


if 'ASSBOT_DOCKER' in os.environ:
    os.chdir('/usr/games/assbot')

    if __name__ == "__main__":
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
