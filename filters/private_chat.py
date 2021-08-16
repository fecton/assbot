from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsGroup(BoundFilter):
    async def check(self, message: types.Message):
        if message.chat.type != types.ChatType.PRIVATE:
            return True
        await message.answer("⛔️ Працює лишу у групах!")
        return False
