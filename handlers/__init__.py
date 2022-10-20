from loader import logger

from .errors import dp
from .groups import dp
from .users import dp

__all__ = ["dp"]

logger.debug('Handlers loaded successfully!')
