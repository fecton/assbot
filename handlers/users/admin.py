import sqlite3
import re

import aiogram

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.markdown import bold, italic, code
from aiogram.utils.markdown import escape_md as esc
from loader import dp, logger

from data.functions import AssCore, user_input
from data.long_messages import long_messages
from filters import IsAdmin
from loader import db, bot
from states import Ask_Text


@dp.message_handler(IsAdmin(), commands="admin")
async def show_admin_help(message: types.Message):
    """
    Admin help
    """
    await message.answer(esc(long_messages["admin"]))



@dp.message_handler(IsAdmin(), commands="notify")
async def get_message_to_notify(message: types.Message):
    """
    The state takes a next user message for notify 
    """
    
    t = "😇 Будь ласка, введіть деяку новину одним повідомленням"
    await message.answer(t)
    await Ask_Text.no_text.set()


@dp.message_handler(IsAdmin(), state=Ask_Text.no_text)
async def are_you_sure(message: types.Message, state: FSMContext):
    """
    Takes message from previos handler and asks a confirmation
    """
    
    await state.update_data(text=message.text)

    t = "Ви впевнені у своєму повідомленні? y/n (так/ні)"

    await message.answer(t)
    await Ask_Text.with_text.set()


@dp.message_handler(IsAdmin(), state=Ask_Text.with_text)
async def notify_all_groups(message: types.Message, state: FSMContext):
    """
    Notify all groups in the database with admin's message
    """

    text = (await state.get_data())["text"]

    if message.text in ["y", "yes", "так", "т"]:
        query = "SELECT * FROM `groups_name`"
        groups_list = db.execute(query, fetchall=True)

        for group_id in groups_list: 
            try:
                await bot.send_message(group_id[0], text, disable_web_page_preview=False)
            except aiogram.exceptions.Unauthorized:
                continue
            except aiogram.exceptions.ChatNotFound:
                continue
            except aiogram.exceptions.MigrateToChat as err:
                await bot.send_message(err.migrate_to_chat_id, text, disable_web_page_preview=False)

        t = "Повідомлення було відправлене группам!"
    else:
        t = "Процедура скасована!"

    await message.answer(esc(t))

    await state.reset_state()



@dp.message_handler(IsAdmin(), commands="groups")
async def show_groups(message: types.Message):
    """
    This function shows all registered groups (id and its)
    """
    
    query = "SELECT * FROM `groups_name`"
    try:
        groups_info = db.execute(query, fetchall=True)
    except sqlite3.OperationalError:
        logger.debug("[!] The table `groups_name` doesn't exist or was deleted, created new one")

        db.create_groups_name_table()
        db.insert_into_groups_name((message.chat.id, message.chat.title))

        groups_info = db.execute(query, fetchall=True)

    groups_dict = dict()

    for group in groups_info:
        groups_dict[group[0]] = group[1]

    output_message = f"✅ {bold('TABLES')}\n" + esc("-") * 16 + "\n"
    if len(groups_dict.keys()) != 0:
        for key in groups_dict.keys():
            output_message += f"{code(str(key))}" + " : " + esc(groups_dict[key]) + "\n"
        output_message += esc("-") * 16
        await message.answer(output_message)
    else:
        t = "⛔️ Ще нема груп!"
        await message.answer(esc(t))


@dp.message_handler(IsAdmin(), commands="bl")
async def show_blacklisted_users(message: types.Message):
    """
    This function shows all banned users in a group
    """
    
    group_id = user_input(message, "/bl")

    if group_id == "":
        t = "⛔️ Ти забув ввести ID группи!"
        await message.answer(esc(t))
    else:
        if group_id == "self":
            group_id = message.chat.id
        else:
            if re.search(r"[A-Za-z]", group_id):
                t = "⛔️ Вибач, але не знаю такої групи."
                await message.answer(esc(t))
                return

        try:
            query = """
                SELECT * FROM `%s` WHERE blacklisted=1
            """ % group_id
            users_data = db.execute(query, fetchall=True)
        except sqlite3.OperationalError:
            t = "⛔️ Вибач, але не знаю такої групи."
            await message.answer(esc(t))
            return

        if not users_data:
            t = "✅ Нема заблокованих користувачів!"
            await message.answer(esc(t))
        else:
            output_message = f"👥 Group: <code>{group_id}</code>\n"
            output_message += "ІД : Юзернейм : Ім'я гравця\n\n"

            users_count = 0
            for user_data in users_data:
                users_count += 1
                if user_data[1] == user_data[2]:
                    output_message += f"💢 {user_data[0]} :  {user_data[1]}\n"
                else:
                    output_message += f"💢 {user_data[0]} :  @{user_data[1]} : {user_data[2]}\n"

            output_message += '\n📌 Усього: '

            if users_count == 1:
                output_message += "1 гравець"
            else:
                output_message += "%d гравців" % users_count
            await message.answer(output_message)


@dp.message_handler(IsAdmin(), commands="ban")
async def ban(message: types.Message):
    """
    This header reads "/ban" string and after a space user id
    after that updates user's column "blacklisted" to 1 (user will be banned)
    """
    
    if message.reply_to_message is not None:
        user_to_ban = message.reply_to_message.from_user.id
        ban_group = message.chat.id
        try:
            # if group exists
            try:
                query = """
                    SELECT * FROM `%s`
                """ % ban_group
                db.execute(query, commit=True)
            except sqlite3.OperationalError:
                t = "⛔️ Не існує такої групи!"
                await message.answer(esc(t))
                return
        except ValueError:
            t = "⛔️ Не знаю таких гравців"
            await message.answer(esc(t))
    else:
        info = user_input(message, "/ban").split(" ")

        if len(info) != 2:
            t = "⛔️ Невірний формат!"
            await message.answer(esc(t)); return

        # select current group
        if info[0] == "self":
            ban_group = message.chat.id
        else:
            ban_group = info[0]

        # select yourself
        if info[1] == "self":
            user_to_ban = message.from_user.id
        else:
            user_to_ban = info[1]

        if info[0] != "self" and info[1] != "self":
            if re.search(r"[A-Za-z]", info[0]) or re.search(r"[A-Za-z]", info[1]):
                t = "⛔️ Невірний формат!"
                await message.answer(esc(t))
                return

        user_to_ban, ban_group = int(user_to_ban), int(ban_group)

        if not user_to_ban:
            t = "⛔️ Можливо ти щось забув?"
            await message.answer(t)
            return

    query = """
        SELECT * FROM `%d` WHERE user_id=%d
    """ % (ban_group, user_to_ban)

    user = db.execute(query, fetchone=True)[0]
    # if user exists
    if user:
        query = """
            UPDATE `%d` SET blacklisted=1 WHERE user_id=%d
        """ % (ban_group, user_to_ban)
        db.execute(query, commit=True)
        t = "✅ Користувач отримав по своїй сідничці!"
    else:
        t = "⛔️ Користувач має бути зарегестрованим у грі!"

    await message.answer(esc(t))

@dp.message_handler(IsAdmin(), commands="ub")
async def unban(message: types.Message):
    """
    This handler unban user by the argument (set blacklisted to 0)
    """

    if message.reply_to_message is not None:
        group_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
    else:
        info = user_input(message, "/ub").split(" ")
        if len(info) != 2:
            t = "⛔️ Невірний формат!"
            await message.answer(t)
            return

        # select current group
        if info[0] == "self" and message.chat.type != "private":
            group_id = message.chat.id
        else:
            group_id = info[0]
            if re.search(r"[A-Za-z]", group_id):
                t = "⛔️ Невірний формат!"
                await message.answer(t)
                return
            group_id = int(group_id)

        # select yourself
        if info[1] == "self":
            user_id = message.from_user.id
        else:
            user_id = info[1]
            if re.search(r"[A-Za-z]", user_id):
                t = "⛔️ Невірний формат!"
                await message.answer(t)
                return
            user_id = int(user_id)

    try:
        query = """
            SELECT blacklisted FROM `%d` WHERE user_id=%d
        """ % (group_id, user_id)

        user_is_blacklisted = db.execute(query, fetchone=True)[0]

        if user_is_blacklisted:
            query = """
                UPDATE `%d` SET blacklisted=0, spamcount=0 WHERE user_id=%d
            """ % (group_id, user_id)
            db.execute(query, commit=True)
            t = "✅ Користувач може повернутися до гри!"
        else:
            t = "❌ Користувач не заблокований!"
        await message.answer(esc(t))

    except sqlite3.OperationalError:
        t = "⛔️ Дана группа не існує!"
        await message.answer(esc(t))


# SHOW REPORTS FROM TABLE `reports` in simple form
@dp.message_handler(IsAdmin(), commands="reports")
async def show_reports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """
    
    query = "SELECT * FROM `reports`"
    users = db.execute(query, fetchall=True)

    if users:  # if users exist in group's table
        output_message = "NAME:MESSAGE\n\n"
        for user in users:
            output_message += f"🚩 {user[4]} : {user[5]}\n"
        await message.answer(esc(output_message))
    else:
        t = "⛔️ Ще нема звітів"
        await message.answer(t)


# SHOW REPORTS FROM TABLE `reports` in detailed form
@dp.message_handler(IsAdmin(), commands="dreports")
async def show_detailed_reports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """
    
    query = "SELECT * FROM `reports`"
    users = db.execute(query, fetchall=True)

    if users:  # if users exist in group's table
        output_message = "GRPID:GRPNAME:USERRID:USERNAME:NAME:MESSAGE\n\n"
        for user in users:
            if user[0] == user[2]:
                output_message += f"🚩 {user[0]} : {user[1]} : @{user[3]} : {user[4]} : {user[5]}\n\n"
            else:
                output_message += f"🚩 {user[0]} : {user[1]} : {user[2]} : @{user[3]} : {user[4]} : {user[5]}\n\n"
        await message.answer(esc(output_message))
    else:
        t = "⛔️ Ще нема звітів"
        await message.answer(esc(t))


@dp.message_handler(IsAdmin(), commands="clear")
async def clear_reports(message: types.Message):
    """
    This function delete all writes in the table `reports` by
    """
    
    query = "SELECT * FROM `reports`"
    data = db.execute(query, fetchone=True)

    if data:
        query = """
            DELETE FROM `reports`
        """
        db.execute(query, commit=True)

        t = "✅ Звіти повністю очищені!" 
    else:
        t = "⛔️ Навіщо мені очищати пусту скриньку?"

    await message.answer(esc(t))


@dp.message_handler(IsAdmin(), commands="show")
async def show_users(message: types.Message):
    """
    This function send message with all user from group via group id
    :group_id: Yeah, it's Group_id
    """
    
    group_id = user_input(message, "/show")

    if group_id == "self":
        group_id = message.chat.id
    else:
        if re.search(r"[A-Za-z]", group_id) or not group_id:
            t = "⛔️ Невірний формат!"
            await message.answer(esc(t))
            return
        group_id = int(group_id)

    if group_id:

        # (user_id, username, firstname, length, endtime, spamcount, blacklisted)
        try:
            query = "SELECT * FROM `%d`" % group_id
            users = db.execute(query, fetchall=True)
            output_message = f"👥 Група: {code(groupd_id)}\n"
            output_message += "ІД:Нікнейм:Ім'я:Довжина:Спам:Можливість грати\n\n"

            user_count = 0
            for user in users:
                user_count += 1
                user = AssCore(user)
                if user.blacklisted == 1:  # if blacklisted
                    blacklisted = "❌"
                else:
                    blacklisted = "✅"
                
                if(user.username == "None"):
                    output_message += f" ▶️ {code(user.id)} : {bold(Відсутній)} : {bold(user.name)}"
                else:
                    output_message += f" ▶️ {code(user.id)} : {bold('@'+user.username)} : {bold(user.name)}"

                output_message += f" : {user.length} : {user.spamcount} : {blacklisted}\n"

            output_message += "\n📌 Усього: "
            if user_count == 1:
                output_message += "1 гравець"
            else:
                output_message += f"{user_count} гравців"

            await message.answer(output_message)
        except sqlite3.OperationalError:
            t = "⛔️ Такої групи не існує"
            await message.answer(t)
    else:
        t = "⛔️ Ти забув про ідентифікатор групи!"
        await message.answer(t)
