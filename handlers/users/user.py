from aiogram import types
from aiogram.utils.markdown import escape_md as esc
from loader import dp, db
from data.config import SUPER_USERS, USER_RATE_LIMIT
from data.functions import user_input
from data.structures import ReportStructure
from utils.set_rate_limit import rate_limit


# REPORT "message"
@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(commands="r")
async def report(message: types.Message):
    """
    This handler reads your message after "/r " and write it in the table `reports`
    """
    
    m = user_input(message, "/r")

    if len(m) < 10:
        if len(m.strip()) == 0:
            t = "Ти забув уввести свій звіт!"
        else:
            t = "Звіт дуже малий!"
        await message.reply(esc(t))

    elif m[2] == "@" or "--" in m or "#" in m:
        t = "Невірний формат!"
        await message.reply(esc(t))
    else:
        Rdata = ReportStructure(message.chat.id, message.chat.title, message.from_user.id, message.from_user.username, message.from_user.first_name, m)

        if Rdata.chat_title is None:
            Rdata.chat_title = "Private"
        if Rdata.user_name is None:
            Rdata.user_name = "N/A"

        db.insert_into_reports(Rdata)

        t = "Дякуємо за звіт! 💛"
        await message.reply(esc(t))

        for admin in SUPER_USERS:
            # if user doesn't have @username it will sent his name
            text = "[R] Надісланий звіт від %s, детальніше: /reports, /dreports"
            if Rdata.user_name == "N/A":
                await dp.bot.send_message(
                    admin,
                    esc(text % Rdata.user_firstname)
                )
            else:
                await dp.bot.send_message(
                    admin,
                    esc(text % ("@"+Rdata.user_name))
                )
