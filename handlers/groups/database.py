import sqlite3

from loader import dp
from aiogram import types
from data.config import DB_NAME
from filters import IsJoined, IsLeft


@dp.message_handler(IsJoined(), content_types="new_chat_members")
async def bot_joined(message: types.Message):
    from database.create import CREATE_table_groups
    from database.insert import INSERT_into_groups_name

    group_id = message.chat.id
    db = sqlite3.connect(DB_NAME)

    # append new table to the database
    db.execute(CREATE_table_groups % group_id)
    # add short info about group in the table `groups_name` for command /groups
    db.execute(INSERT_into_groups_name, (group_id, message.chat.title))

    db.commit()
    db.close()

    print("[+] Table with name '%d' (%s) created successfully!" % (group_id, message.chat.title))


@dp.message_handler(IsLeft(), content_types="left_chat_member")
async def bot_left(message: types.Message):
    chat_id = message.chat.id
    
    db = sqlite3.connect(DB_NAME)

    db.execute("DROP TABLE `%d`" % chat_id)
    db.execute("DELETE FROM `groups_name` WHERE group_id=%d" % chat_id)

    db.commit()
    db.close()

    print("[+] The group %d has deleted!" % chat_id)
