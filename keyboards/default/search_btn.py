from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

search_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Смотреть анкеты")
        ]
    ],
    resize_keyboard=True,
)