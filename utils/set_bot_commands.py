from aiogram import types, Dispatcher
from cfg import long_messages

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
