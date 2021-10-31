#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Open-Source AssBot 2021
# ------------------------------
#
# Made with love by Fecton
# https://github.com//fecton
#
# ------------------------------
# Enjoy using! ^_^

__version__ = "1.5.2"

from aiogram import Dispatcher

import middlewares


async def on_startup(dp: Dispatcher):
    from utils.notify_admins import on_startup_notify
    from utils.set_bot_commands import set_default_commands

    middlewares.setup(dp)
    await set_default_commands(dp)
    await on_startup_notify(dp)


if __name__ == "__main__":
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
