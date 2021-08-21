from aiogram import Dispatcher
from .private_chat import IsGroup
from .is_admin import IsAdmin
from .join_left import IsJoined, IsLeft

def setup(dp: Dispatcher):
    pass