import asyncio
from aiogram import types

default_delay   = 10


async def answer(message: types.Message, t: str, delay: int = default_delay):
    """
    message.answer with timeout and auto deletion the message

    message: a message taked by handler
    t: text
    delay: timeout for message
    """

    sentM = (await message.answer(t))
    await asyncio.sleep(delay)
    await sentM.delete()
    await message.delete()


async def reply(message: types.Message, t: str, delay: int = default_delay):
    """
    message.reply with timeout and auto deletion the message

    message: a message taked by handler
    t: text
    delay: timeout for message
    """

    sentM = (await message.reply(t))
    await asyncio.sleep(delay)
    await sentM.delete()
    await message.delete()