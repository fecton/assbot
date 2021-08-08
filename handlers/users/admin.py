import sqlite3
from aiogram import types
from loader import dp

from data.config import long_messages, SUPER_USERS, DB_NAME
from data.functions import user_input, Ass_Info_Obj


@dp.message_handler(commands="admin")
async def send_adminhelp(message: types.Message):
    if message.from_user.id in SUPER_USERS:
        await message.answer(long_messages["admin"])


@dp.message_handler(commands="groups")
async def show_groups(message: types.Message):
    """
    This function shows all registered in the game groups (its id and its name)
    """

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        try:
            groups_info = db.cursor().execute("SELECT * FROM `groups_name`").fetchall()
        except sqlite3.OperationalError:
            from database.create import CREATE_table_groups_name
            from database.insert import INSERT_into_groups_name
            print("[!] The table `groups_name` doesn't exist or was deleted, created new one")
            db.execute(CREATE_table_groups_name)

            db.execute(INSERT_into_groups_name, (message.chat.id, message.chat.title))

            groups_info = db.cursor().execute("SELECT * FROM `groups_name`").fetchall()

        db.close()

        groups_dict = dict()

        for group in groups_info:
            groups_dict[group[0]] = group[1]

        output_message = "✅ __*TABLES*__\n" + "=" * 16 + "\n"
        for key in groups_dict.keys():
            output_message += "`%s`" % str(key) + " : " + groups_dict[key] + "\n"

        await message.reply(output_message, parse_mode="Markdown")


@dp.message_handler(commands="bl")
async def show_blacklisted_users(message: types.Message):
    """
    This function shows all banned users in a group
    """

    if message.from_user.id in SUPER_USERS:  # if is admin
        group_id = user_input(message, "/bl")

        if group_id == "":
            await message.reply("⛔️ Ти забув ввести ID группи!")
        else:
            if group_id == "self":
                group_id = message.chat.id
            else:
                try:
                    group_id = int(group_id)
                except ValueError:
                    await message.reply("⛔️ Вибач, але не знаю такої групи.")
                    return

            db = sqlite3.connect(DB_NAME)
            try:
                cursor = db.execute("""
                    SELECT * FROM `{0}` WHERE blacklisted=1
                """.format(group_id))
                users_data = cursor.fetchall()
            except sqlite3.OperationalError:
                await message.reply("⛔️ Вибач, але не знаю такої групи.")
                db.close()
                return
            finally:
                db.close()

            if not users_data:
                await message.reply("✅ Нема заблокованих користувачів!")
            else:
                output_message = f"👥 Group: <code>{group_id}</code>\n"
                output_message += "ID : USERNAME : NAME\n\n"

                users_count = 0
                for user_data in users_data:
                    users_count += 1
                    if user_data[1] == user_data[2]:
                        output_message += f"💢 {user_data[0]} :  {user_data[1]}\n"
                    else:
                        output_message += f"💢 {user_data[0]} :  @{user_data[1]} : {user_data[2]}\n"
                if users_count == 1:
                    output_message += "\n📌 Totally: 1 user"
                else:
                    output_message += "\n📌 Totally: %d users" % users_count
                await message.reply(output_message, parse_mode="HTML")


@dp.message_handler(commands="ban")
async def ban(message: types.Message):
    """
    This header reads "/ban" string and after a space user id
    after that updates user's column "blacklisted" to 1 (user will be banned)
    """

    if message.from_user.id in SUPER_USERS:  # if is admin
        info = user_input(message, "/ban").split(" ")
        if len(info) != 2:
            await message.reply("⛔️ Невірний формат!")
            return

        # select current group
        if info[0] == "self":
            ban_group = message.chat.id
        else:
            ban_group = int(info[0])

        # select yourself
        if info[1] == "self":
            user_to_ban = message.from_user.id
        else:
            user_to_ban = int(info[1])

        if not user_to_ban:
            await message.reply("⛔️ Можливо ти щось забув?")
        else:
            try:
                user_id = user_to_ban
                group_id = ban_group
                db = sqlite3.connect(DB_NAME)

                # if group exists
                try:
                    db.execute(f"""
                        SELECT * FROM `{group_id}`
                    """)
                except sqlite3.OperationalError:
                    await message.reply("⛔️ Не існує такої групи!")
                    return

                user = db.execute(f"""
                    SELECT * FROM `{group_id}` WHERE user_id={user_id}
                """).fetchone()

                # if user exists
                if user:
                    db.execute(f"""
                        UPDATE `{group_id}` SET blacklisted=1 WHERE user_id={user_id}
                    """)
                    await message.answer("✅ Користувач отримав по своїй сідничці!")
                else:
                    await message.reply("⛔️ Користувач має бути зарегестрованим у грі!")

                db.commit()
                db.close()

            except ValueError:
                await message.reply("⛔️ Не знаю таких гравців")
    else:
        await message.reply("⛔️ Працює лишу в групах!")


@dp.message_handler(commands="ub")
async def unban(message: types.Message):
    """
    This handler unban user by the argument (set blacklisted to 0)
    """

    if message.from_user.id in SUPER_USERS:  # if is admin
        info = user_input(message, "/ub").split(" ")
        if len(info) != 2:
            await message.reply("⛔️ Невірний формат!")
            return

            # select current group
        if info[0] == "self" and message.chat.type != "private":
            group_id = message.chat.id
        else:
            group_id = info[0]

        # select yourself
        if info[1] == "self":
            user_id = message.from_user.id
        else:
            user_id = info[1]

        if not user_id:
            await message.reply("⛔️ Ти забув уввести ID заблокованого користувача!")
        else:
            if user_id != "self" or group_id != "self":
                try:
                    user_id, group_id = int(user_id), int(group_id)
                except ValueError:
                    await message.reply("⛔️ Невірний формат!")
                    return

            db = sqlite3.connect(DB_NAME)
            db.execute("""
                UPDATE `{0}` SET blacklisted=0, spamcount=0 WHERE user_id={1}
            """.format(group_id, user_id))

            db.commit()
            db.close()

            await message.reply("✅ Користувач може повернутися до гри!")
    else:
        await message.reply("⛔️ Працює лише в групах!")


# SHOW REPORTS FROM TABLE `reports` in simple form
@dp.message_handler(commands="reports")
async def show_reports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        users = db.execute("SELECT * FROM `reports`").fetchall()

        db.close()

        if users:  # if users exist in group's table
            output_message = "USERNAME : NAME : MESSAGE\n\n"
            for user in users:
                output_message += f"🚩 {user[4]} : {user[5]}\n"
            await message.reply(output_message)
        else:
            await message.reply("⛔️ Ще нема звітів")


# SHOW REPORTS FROM TABLE `reports` in detailed form
@dp.message_handler(commands="dreports")
async def show_dreports(message: types.Message):
    """
    This function show all rows from table `reports` and send it in one message
    """

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        users = db.execute("SELECT * FROM `reports`").fetchall()

        db.close()

        if users:  # if users exist in group's table
            output_message = "USERNAME : NAME : MESSAGE\n\n"
            for user in users:
                output_message += f"🚩 {user[0]} : {user[1]} : {user[2]} : {user[3]} : {user[4]} : {user[5]}\n\n"
            await message.reply(output_message)
        else:
            await message.reply("⛔️ Ще нема звітів")


# CLEAR ALL REPORTS FROM TABLE `reports`
@dp.message_handler(commands="clear")
async def clear_reports(message: types.Message):
    """
    This function delete all writes in the table `reports` by
    """

    if message.from_user.id in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)
        data = db.execute("SELECT * FROM `reports`").fetchone()

        if data:
            db.execute("""
                DELETE FROM `reports`
            """)
            db.commit()
            db.close()

            await message.reply("✅ Звіти повністю очищені!")
        else:
            await message.reply("⛔️ Навіщо мені очищати пусту скриньку?")


@dp.message_handler(commands="show")
async def show_users(message: types.Message):
    """
    This function send message with all user from group via group id
    :group_id: Yeah, it's Group_id
    """
    group_id = user_input(message, "/show")

    if message.from_user.id in SUPER_USERS:
        if group_id == "self":
            group_id = message.chat.id
        if group_id:
            try:
                group_id = int(group_id)
                db = sqlite3.connect(DB_NAME)
                # (user_id, username, firstname, length, endtime, spamcount, blacklisted)
                try:
                    USERS = db.execute("SELECT * FROM `%d`" % group_id).fetchall()
                    output_message = "👥 Group: <code>%s</code>\n" % group_id
                    output_message += "ID : USERNAME:NAME : SPAMCOUNT: IS_BANNED\n\n"

                    user_count = 0
                    for user in USERS:
                        user_count += 1
                        user = Ass_Info_Obj(user)
                        if user.blacklisted == 1:  # if blacklisted
                            blacklisted = "✅"
                        else:
                            blacklisted = "❌"
                        output_message += f" ▶️ <code>{user.id}</code> : <b>{user.username}</b> : <b>{user.name}</b>"\
                                          f" : {user.spamcount} : {blacklisted}\n"

                    if user_count == 1:
                        output_message += "\n📌 Totally: 1 user"
                    else:
                        output_message += f"\n📌 Totally: {user_count} users"

                    await message.reply(output_message, parse_mode="HTML")
                except sqlite3.OperationalError:
                    await message.reply("⛔️ Такої групи не існує")
                finally:
                    db.close()

            except ValueError:
                await message.reply("⛔️ Невірний формат!")
        else:
            await message.reply("⛔️ Ти забув про ідентифікатор групи!")
