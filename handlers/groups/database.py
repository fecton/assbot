import sqlite3

from loader import dp
from data.config import DB_NAME


@dp.message_handler(content_types="new_chat_members")
@dp.message_handler(lambda message: message.from_user.id == 1777031958)
async def start(message):
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
