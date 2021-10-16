from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Вернуться назад")
        ]
    ],
    resize_keyboard=True,
)