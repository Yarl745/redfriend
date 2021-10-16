from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

show_likes_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Показать")
        ]
    ],
    resize_keyboard=True,
)