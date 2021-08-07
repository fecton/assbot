from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp

from loader import dp
from data.config import long_messages


@dp.message_handler(CommandStart())
async def send_start(message: types.Message):
    await message.answer(long_messages["start"])


@dp.message_handler(CommandHelp())
async def send_help(message: types.Message):
    await message.answer(long_messages["help"])


@dp.message_handler(commands="about")
async def send_about(message: types.Message):
    await message.answer(long_messages["about"], disable_web_page_preview=True)

