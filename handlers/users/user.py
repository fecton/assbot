from aiogram import types
from loader import dp, db
from data.config import SUPER_USERS, USER_RATE_LIMIT
from data.functions import user_input
from utils.set_rate_limit import rate_limit


# REPORT "message"
@rate_limit(USER_RATE_LIMIT*2)
@dp.message_handler(commands="r")
async def report(message: types.Message):
    """
    This handler reads your message after "/r " and write it in the table `reports`
    """

    report_message = user_input(message, "/r")

    if len(report_message) < 10:
        if len(report_message.strip()) == 0:
            await message.reply("Ти забув уввести свій звіт!")
        else:
            await message.reply("Звіт дуже малий!")
    elif message.text[2] == "@" or "--" in message.text or "#" in message.text:
        await message.reply("Невірний формат!")
    else:

        data = [
            message.chat.id, 
            message.chat.title,
            message.from_user.id, 
            message.from_user.username,
            message.from_user.first_name, 
            report_message
        ]

        # if it's personal message then message.chat will be marked "Personal message"

        if data[1] is None:  # a private chat or a group
            data[1] = "Private"
        if data[3] is None:  # if a user doesn't have username
            data[3] = "N/A"

        db.insert_into_reports(data)

        await message.reply("Дякуємо за звіт! 💛")

        for admin in SUPER_USERS:
            # if user doesn't have @username it will sent his name
            text = "[R] Надісланий звіт від %s, детальніше: /reports, /dreports"
            if data[3] == "N/A":
                await dp.bot.send_message(
                    admin,
                    text % data[4]
                )
            else:
                await dp.bot.send_message(
                    admin,
                    text % data[3]
                )
