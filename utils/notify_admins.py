from time import asctime
from aiogram import Dispatcher
from aiogram.utils.markdown import escape_md as esc
from data.config import logger

from data.config import SUPER_USERS, long_messages

notify_m = long_messages["notify_admins"]

async def on_startup_notify(dp: Dispatcher):
    bot_name = (await dp.bot.get_me()).first_name
    for admin in SUPER_USERS:
        try:
            await dp.bot.send_message(
                admin,
                esc(notify_m % (bot_name, asctime()))
            )
        except Exception as err:
            logger.error(err)
