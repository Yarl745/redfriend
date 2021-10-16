from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

disable_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Да, отключить анкету"),
            KeyboardButton("Нет, вернуться назад"),
        ]
    ],
    resize_keyboard=True,
)