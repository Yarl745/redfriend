from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

how_work_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Как ты работаешь? 🤔")
        ]
    ],
    resize_keyboard=True,
)