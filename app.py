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

__version__ = "1.5"

from utils.set_bot_commands import set_default_commands
from aiogram import Dispatcher


async def on_startup(dp: Dispatcher):
    import filters
    filters.setup(dp)

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await set_default_commands(dp)


if __name__ == "__main__":
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
