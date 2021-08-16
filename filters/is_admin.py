from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from data.config import SUPER_USERS


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id in SUPER_USERS:
            return True
        return False
