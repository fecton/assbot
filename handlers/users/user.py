import sqlite3

from aiogram import types
from loader import dp
from data.config import DB_NAME, SUPER_USERS
from data.functions import user_input


# REPORT "message"
@dp.message_handler(commands="r")
async def report(message: types.Message):
    """
    This handler reads your message after "/r " and write it in the table `reports`
    """

    report_message = user_input(message, "/r")

    if len(report_message) < 10:
        if len(report_message.strip()) == 0:
            await message.reply("⛔️ Ти забув уввести свій звіт!")
        else:
            await message.reply("⛔️ Звіт дуже малий!")
    elif message.text[2] == "@":
        await message.reply("⛔️ Невірний формат!")
    elif "--" in message.text or "#" in message.text:
        await message.reply("⛔️ Невірний формат!")
    else:

        data = [message.chat.id, message.chat.title,
                message.from_user.id, message.from_user.username,
                message.from_user.first_name, report_message]

        # if it's personal message then message.chat will be marked "Personal message"

        if data[1] is None:
            data[1] = "Private"
        if data[3] is None:
            data[3] = "N/A"

        db = sqlite3.connect(DB_NAME)
        from database.insert import INSERT_into_reports

        db.execute(INSERT_into_reports, data)

        db.commit()
        db.close()
        await message.reply("Дякуємо за звіт! 💛")

        print("[R] A report had sent!")

        for admin in SUPER_USERS:
            if data[3] == "N/A":
                await dp.bot.send_message(admin, "[R] Надісланий звіт від %s, детальніше: /reports" % data[4])
            else:
                await dp.bot.send_message(admin, "[R] Надісланий звіт від @%s, детальніше: /reports" % data[3])
