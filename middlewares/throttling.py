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


    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        # if handler exists that try to get attributes
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(
                handler,
                "throttling_key",
                f"{self.prefix}_{handler.__name__}")
        # else it sets itself attributes
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        # is message throttled (is flood)
        try:
            # checks else it raises an exception
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # user is not an admin?
            is_not_admin = not (await IsAdmin().check(message))
            if is_not_admin:
                await self.message_throttled(message, t)  # wait a little
                raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        await asyncio.sleep(10)
