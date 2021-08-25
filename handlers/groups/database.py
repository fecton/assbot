from loader import dp
from aiogram import types
from filters import IsJoined, IsLeft
from utils.db_core import DbCore


@dp.message_handler(IsJoined(), content_types="new_chat_members")
async def bot_joined(message: types.Message):

    group_id = message.chat.id
    db = DbCore()
    # append new table to the database
    db.create_group_table(group_id)
    # add short info about group in the table `groups_name` for command /groups
    db.insert_into_groups_name((group_id, message.chat.title))

    print("[+] Table with name '%d' (%s) created successfully!" % (group_id, message.chat.title))


@dp.message_handler(IsLeft(), content_types="left_chat_member")
async def bot_left(message: types.Message):
    chat_id = message.chat.id

    db = DbCore()
    db.execute("DROP TABLE `%d`" % chat_id)
    db.execute("DELETE FROM `groups_name` WHERE group_id=%d" % chat_id)

    print("[+] The group %d has deleted!" % chat_id)
