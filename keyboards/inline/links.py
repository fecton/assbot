from aiogram import types
from config import long_messages


about_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton("🕸 Website", url=long_messages["links"]["website"])
        ],
        [
            types.InlineKeyboardButton("⚫️ GitHub", url=long_messages["links"]["github"]),
        ],
        [
            types.InlineKeyboardButton("🔵 Telegram Channel", url=long_messages["links"]["telegram_channel"]),
        ],
    ],
    resize_keyboard=True
)
