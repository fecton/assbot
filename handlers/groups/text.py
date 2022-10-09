from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from aiogram.utils.markdown import escape_md as esc

from loader import dp
from data.config import USER_RATE_LIMIT, long_messages
from utils.set_rate_limit import rate_limit

from keyboards.inline import about_keyboard


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(CommandStart())
async def send_start(message: types.Message):
    await message.answer(esc(long_messages["start"]))


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(CommandHelp())
async def send_help(message: types.Message):
    await message.answer(esc(long_messages["help"]))


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(commands="about")
async def send_about(message: types.Message):
    await message.answer(
        esc(long_messages["about"]), 
        disable_web_page_preview=True, 
        reply_markup=about_keyboard,
    )
