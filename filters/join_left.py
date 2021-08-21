from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsJoined(BoundFilter):
    async def check(self, message: types.Message):
        from loader import dp
        
        bot_id = (await dp.bot.get_me())["id"]
        users_id = message.new_chat_members
        
        for user_id in users_id:
            if user_id["id"] == bot_id:
                return True
        return False


class IsLeft(BoundFilter):
    async def check(self, message: types.Message):
        from loader import dp
        
        bot_id = (await dp.bot.get_me())["id"]
        user_id = message.left_chat_member["id"]
        
        if bot_id == user_id:
            return True
        return False
