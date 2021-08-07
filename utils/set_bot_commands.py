from aiogram import types

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "привітатися з ботом"),
        types.BotCommand("ass", "грати"),
        types.BotCommand("luck", "казино"),
        types.BotCommand("leave", "залишити гру"),
        types.BotCommand("statistic", "рейтинг"),
        types.BotCommand("help", "довідка"),
    ])

