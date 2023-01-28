from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from aiogram.utils.markdown import escape_md as esc

from loader import dp
from config import USER_RATE_LIMIT, long_messages
from utils.set_rate_limit import rate_limit

from keyboards.inline import about_keyboard

from .funcs import answer
from filters import IsGroup


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(CommandStart())
async def send_start(message: types.Message):
    is_private = not await(IsGroup().check(message))
    if is_private:
        await message.answer(esc(long_messages["start"]))
    else:
        await answer(message, esc(long_messages["start"]))


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(CommandHelp())
async def send_help(message: types.Message):
    is_private = not await(IsGroup().check(message))
    if is_private:
        await message.answer(esc(long_messages["help"]))
    else:
        await answer(message, esc(long_messages["help"]))


@rate_limit(USER_RATE_LIMIT)
@dp.message_handler(commands="about")
async def send_about(message: types.Message):
    await message.answer(
        esc(long_messages["about"]), 
        disable_web_page_preview=True, 
        reply_markup=about_keyboard,
    )
