
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from data.config import SUPER_USERS
from loader import dp


class IsAdmin(BoundFilter):
    """
    Filters users if it is an admin
    """
    async def check(self, message: types.Message):
        if message.from_user.id in SUPER_USERS:
            return True
        return False


class IsJoined(BoundFilter):
    """
    The filter works when the bot joins to a group
    """
    async def check(self, message: types.Message):
        bot_id = (await dp.bot.get_me())["id"]
        users_id = message.new_chat_members

        for user_id in users_id:
            if user_id["id"] == bot_id:
                return True
        return False


class IsLeft(BoundFilter):
    """
    The filter works when the bot lefts to a group
    """
    async def check(self, message: types.Message):

        bot_id = (await dp.bot.get_me())["id"]
        user_id = message.left_chat_member["id"]

        if bot_id == user_id:
            return True
        return False


class IsUser(BoundFilter):
    """
    The filter works when a user (not a bot) joins to a group
    """
    async def check(self, message: types.Message):
        if not message.from_user.is_bot:
            return True
        return False


class IsGroup(BoundFilter):
    """
    The filter tells that it is a private dialog or a group
    """
    async def check(self, message: types.Message):
        if message.chat.type != types.ChatType.PRIVATE:
            return True
        return False





