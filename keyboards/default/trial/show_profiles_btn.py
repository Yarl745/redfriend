from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

show_profiles_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Посмотреть анкеты 👀")
        ]
    ],
    resize_keyboard=True,
)