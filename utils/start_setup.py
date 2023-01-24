from time import asctime
from aiogram import Dispatcher, types
from aiogram.utils.markdown import escape_md as esc
from config import logger, long_messages, SUPER_USERS

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


c_m = long_messages["commands"]

async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", c_m["start"]),
        types.BotCommand("ass", c_m["ass"]),
        types.BotCommand("luck", c_m["luck"]),
        types.BotCommand("leave", c_m["leave"]),
        types.BotCommand("statistic", c_m["statistic"]),
        types.BotCommand("about", c_m["about"]),
        types.BotCommand("help", c_m["help"]),
    ])

