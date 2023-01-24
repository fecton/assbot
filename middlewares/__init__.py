from aiogram import Dispatcher
from .throttling import ThrottlingMiddleware

from loader import logger

def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())

logger.debug('Middleware loaded successfully!')
