import time
from aiogram import Dispatcher

from data.config import SUPER_USERS


async def on_startup_notify(dp: Dispatcher):
    bot_name = (await dp.bot.get_me()).first_name
    for admin in SUPER_USERS:
        try:
            await dp.bot.send_message(
                admin, 
                "Бот '%s' запущен успешно\nВремя запуска: %s" 
                % (bot_name, time.asctime())
            )
        except Exception as err:
            print(err)
