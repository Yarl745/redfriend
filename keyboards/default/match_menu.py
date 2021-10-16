from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

match_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("👍"),
            KeyboardButton("👎"),
        ]
    ],
    resize_keyboard=True,
)