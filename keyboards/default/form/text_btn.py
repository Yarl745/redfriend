from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_text_btn(text: str, with_skip: bool = False):
    keyboard = [
        [
            KeyboardButton(text=text)
        ]
    ]
    if with_skip:
        keyboard.insert(0, [KeyboardButton(text="Пропустить")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)