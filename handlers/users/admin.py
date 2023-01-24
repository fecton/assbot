import sqlite3
import re

import aiogram

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.markdown import bold, italic, code
from aiogram.utils.markdown import escape_md as esc
from loader import dp, logger

from config import AssCore, user_input, long_messages

from filters import IsAdmin
from loader import db, bot
from states import Ask_Text


notify_m = long_messages["notify"]
errors_m = long_messages["errors"]
admin_m = long_messages["admin"]


@dp.message_handler(IsAdmin(), commands="admin")
async def show_admin_help(message: types.Message):
    """
    Admin help
    """
    await message.answer(esc(admin_m["help"]))



@dp.message_handler(IsAdmin(), commands="notify")
async def get_message_to_notify(message: types.Message):
    """
    The state takes a next user message for notify
    """

    await message.answer(esc(notify_m["enter_message"]))
    await Ask_Text.no_text.set()


@dp.message_handler(IsAdmin(), state=Ask_Text.no_text)
async def are_you_sure(message: types.Message, state: FSMContext):
    """
    Takes message from previos handler and asks a confirmation
    """

    await state.update_data(text=esc(message.text))

    await message.answer(esc(notify_m["are_you_sure"]))
    await Ask_Text.with_text.set()


@dp.message_handler(IsAdmin(), state=Ask_Text.with_text)
async def notify_all_groups(message: types.Message, state: FSMContext):
    """
    Notify all groups in the database with admin's message
    """

    confirm_m = list(long_messages["confirmation"].values())

    text = (await state.get_data())["text"]

    if message.text in confirm_m:
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

        t = notify_m["success"]
    else:
        t = notfy_m["cancel"]

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

    output_message = bold(admin_m["groups"]) + "\n" + esc("-") * 16 + "\n"

    if len(groups_dict.keys()) != 0:
        i = 0
        for key in groups_dict.keys():
            a = code(str(key))
            output_message += f"{a}" + " : " + esc(groups_dict[key]) + "\n"
            i += 1
            if i == 100:
                i = 0
                await message.answer(output_message)
                output_message = ""
        output_message += esc("-") * 16
        await message.answer(output_message)
    else:
        await message.answer(esc(errors_m["no_group"]))


@dp.message_handler(IsAdmin(), commands="bl")
async def show_blacklisted_users(message: types.Message):
    """
    This function shows all banned users in a group
    """
    
    group_id = user_input(message, "/bl")

    if group_id == "self":
        group_id = message.chat.id

    try:
        if group_id == "" or re.search(r"[A-Za-z]", group_id):
            raise sqlite3.OperationalError

        query = """
            SELECT * FROM `%s` WHERE blacklisted=1
        """ % group_id
        users_data = db.execute(query, fetchall=True)
    except sqlite3.OperationalError:
        await message.answer(esc(errors_m["unknown_group"]))
        return

    if not users_data:
        await message.answer(esc(errors_m["no_users"]))
    else:
        output_message = admin_m["current_group"] + code(group_id) + "\n" 
        output_message += admin_m["blacklisted_struct"]

        users_count = 0
        for user_data in users_data:
            users_count += 1
            if user_data[1] == user_data[2]:
                output_message += f"💢 {user_data[0]} :  {user_data[1]}\n"
            else:
                output_message += f"💢 {user_data[0]} :  @{user_data[1]} : {user_data[2]}\n"

        output_message += admin_m["totally"]

        if users_count == 1:
            output_message += admin_m["one_player"]
        else:
            output_message += (admin_m["many_players"] % users_count)
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
                await message.answer(esc(errors_m["unknown_group"]))
                return
        except ValueError:
            await message.answer(esc(errors_m["unknown_user"]))
    else:
        info = user_input(message, "/ban").split(" ")

        if len(info) != 2:
            await message.answer(esc(errors_m["illegal_format"]))
            return

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
                await message.answer(esc(errors_m["illegal_format"]))
                return

        user_to_ban, ban_group = int(user_to_ban), int(ban_group)

        if not user_to_ban:
            await message.answer(esc(errors_m["illegal_format"]))
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
        t = admin_m["banned"]
    else:
        t = errors_m["unknown_user"]

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
            await message.answer(esc(errors_m["illegal_format"]))
            return

        # select current group
        if info[0] == "self" and message.chat.type != "private":
            group_id = message.chat.id
        else:
            group_id = info[0]
            if re.search(r"[A-Za-z]", group_id):
                await message.answer(esc(errors_m["illegal_format"]))
                return
            group_id = int(group_id)

        # select yourself
        if info[1] == "self":
            user_id = message.from_user.id
        else:
            user_id = info[1]
            if re.search(r"[A-Za-z]", user_id):
                await message.answer(esc(errors_m["illegal_format"]))
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
            t = admin_m["unbanned"]
        else:
            t = admin_m["isnt_banned"]
        await message.answer(esc(t))

    except sqlite3.OperationalError:
        await message.answer(esc(errors_m["unknown_group"]))


# SHOW REPORTS FROM TABLE `reports` in simple form
@dp.message_handler(IsAdmin(), commands="reports")
async def show_reports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """
    
    query = "SELECT * FROM `reports`"
    users = db.execute(query, fetchall=True)

    if users:  # if users exist in group's table
        output_message = admin_m["reports_struct"]
        for user in users:
            output_message += f"🚩 {user[4]} : {user[5]}\n"
        await message.answer(esc(output_message))
    else:
        t = "⛔️ Ще нема звітів"
        await message.answer(esc(t))


# SHOW REPORTS FROM TABLE `reports` in detailed form
@dp.message_handler(IsAdmin(), commands="dreports")
async def show_detailed_reports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """
    
    query = "SELECT * FROM `reports`"
    users = db.execute(query, fetchall=True)

    if users:  # if users exist in group's table
        output_message = admin_m["dreports_struct"]
        for user in users:
            if user[0] == user[2]:
                output_message += f"🚩 {user[0]} : {user[1]} : @{user[3]} : {user[4]} : {user[5]}\n\n"
            else:
                output_message += f"🚩 {user[0]} : {user[1]} : {user[2]} : @{user[3]} : {user[4]} : {user[5]}\n\n"
        await message.answer(esc(output_message))
    else:
        t = admin_m["empty_reports"]
        await message.answer(esc(t))


@dp.message_handler(IsAdmin(), commands="clear")
async def clear_reports(message: types.Message):
    """
    This function delete all writes in the table `reports` by
    """
    
    query = """
        DELETE FROM `reports`
    """
    db.execute(query, commit=True)

    t = admin_m["reports_cleaned"]

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
        if re.search(r"[A-Za-z]", group_id) or group_id == "":
            await message.answer(esc(errors_m["illegal_format"]))
            return
        else:
            group_id = int(group_id)

    # (user_id, username, firstname, length, endtime, spamcount, blacklisted)
    try:
        query = "SELECT * FROM `%d`" % group_id
        users = db.execute(query, fetchall=True)
        output_message = admin_m["current_group"] + code(group_id) + "\n"
        output_message += admin_m["group_struct"]

        user_count = 0
        for user in users:
            user_count += 1
            user = AssCore(user)

            if user.blacklisted == 1:  # if blacklisted
                blacklisted = "❌"
            else:
                blacklisted = "✅"
            
            if(user.username == "None"):
                output_message += f" ▶️ {code(user.id)} : {bold('Відсутній')} : {bold(user.name)}"
            else:
                output_message += f" ▶️ {code(user.id)} : {bold('@'+user.username)} : {bold(user.name)}"

            output_message += f" : {user.length} : {user.spamcount} : {blacklisted}\n"

        output_message += admin_m["totally"]
        if user_count == 1:
            output_message += admin_m["one_player"]
        else:
            output_message += (admin_m["many_players"] % user_count)

        await message.answer(output_message)
    except sqlite3.OperationalError:
        await message.answer(esc(errors_m["unknown_group"]))
