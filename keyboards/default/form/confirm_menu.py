from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

confirm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Да"),
            KeyboardButton("Изменить анкету"),
        ]
    ],
    resize_keyboard=True,
)