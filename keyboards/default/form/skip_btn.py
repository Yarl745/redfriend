from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

skip_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить")
        ]
    ],
    resize_keyboard=True
)