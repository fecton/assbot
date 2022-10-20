from aiogram.dispatcher.filters.state import StatesGroup, State

class Ask_Text(StatesGroup):
    no_text = State()
    with_text = State()
