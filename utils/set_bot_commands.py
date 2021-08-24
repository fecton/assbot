from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "розпочати"),
        types.BotCommand("ass", "грати"),
        types.BotCommand("luck", "казино"),
        types.BotCommand("leave", "покинути гру"),
        types.BotCommand("statistic", "рейтинг"),
        types.BotCommand("about", "про розробника"),
        types.BotCommand("help", "довідка"),
    ])
