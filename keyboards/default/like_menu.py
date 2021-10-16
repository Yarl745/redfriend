from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

like_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("👍"),
            KeyboardButton("💌"),
            KeyboardButton("👎"),
        ]
    ],
    resize_keyboard=True,
)