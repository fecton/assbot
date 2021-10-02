import asyncio

from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types, Dispatcher
from aiogram.utils.exceptions import Throttled

from filters import IsAdmin


class ThrottlingMiddleware(BaseMiddleware):
    """
    Antiflood middleware
    """

    # initialization middleware its limit (in seconds) and prefix
    def __init__(self, limit=5, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    # process a message
    async def on_process_message(self, message: types.Message, data: dict):
        # get current handler and dispatcher state
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        # if handler exists that try to get attributes
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        # else it sets itself attributes
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        # is message throttled (is flood)
        try:
            await dispatcher.throttle(key, rate=limit)  # checks else it raises an exception
        except Throttled as t:
            is_not_admin = not (await IsAdmin().check(message))  # user is not an admin?
            if is_not_admin: # if not admin
                await self.message_throttled(message, t)  # wait a little
                raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        await asyncio.sleep(10)