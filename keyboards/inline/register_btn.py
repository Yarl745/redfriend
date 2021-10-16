from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

register_btn_callback = CallbackData("register_btn", "action", "empty")

register_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Давай заполню 😉",
                                 callback_data=register_btn_callback.new(
                                     action="register",
                                     empty="-"
                                 ))
        ]
    ]
)