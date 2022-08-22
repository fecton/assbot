import sqlite3

from loader import dp, logger
from aiogram import types
from filters import IsJoined, IsLeft, IsUser
from utils.db_core import DbCore
from utils.set_rate_limit import rate_limit


@dp.message_handler(IsJoined(), content_types="new_chat_members")
async def bot_joined(message: types.Message):
    group_id = message.chat.id

    db = DbCore()
    try:
        db.create_group_table(group_id)
    except sqlite3.OperationalError:
        return
    db.insert_into_groups_name((group_id, message.chat.title))

    logger.debug(f"The table with name '{group_id}' ({message.chat.title}) created successfully!")


@dp.message_handler(IsLeft(), content_types="left_chat_member")
async def bot_left(message: types.Message):
    chat_id = message.chat.id

    db = DbCore()
    db.execute("DROP TABLE `%d`" % chat_id)
    try:
        db.execute(f"DELETE FROM `groups_name` WHERE group_id={chat_id}", commit=True)
    except sqlite3.OperationalError:
        return

    logger.debug(f"The group {chat_id} has deleted!")

@dp.message_handler(IsUser(), content_types="left_chat_member")
async def user_left_the_group_and_game(message: types.Message):
    user_id = message.left_chat_member.id
    chat_id = message.chat.id

    db = DbCore()
    db.execute(f"DELETE FROM `{chat_id}` WHERE user_id={user_id}", commit=True)

    logger.debug(f"The user '{user_id}' from '{chat_id}'")

