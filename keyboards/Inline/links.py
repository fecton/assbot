from aiogram import types
from data.long_messages import long_messages

about_keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

about_keyboard.row(
    types.InlineKeyboardButton("⚫️ GitHub", url=long_messages["links"]["github"])
)

about_keyboard.row(
    types.InlineKeyboardButton("🔵 Telegram Channel", url=long_messages["links"]["telegram_channel"])
)
