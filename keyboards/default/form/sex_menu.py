from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

sex_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Я девушка"),
            KeyboardButton("Я парень"),
        ]
    ],
    resize_keyboard=True,
)