from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

restart_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Начать 😎")
        ]
    ],
    resize_keyboard=True,
)