from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Всех всех"),
            KeyboardButton("Девушек"),
            KeyboardButton("Парней"),
        ]
    ],
    resize_keyboard=True,
)