from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

active_menu_callback = CallbackData("profile_menu", "action", "user_id", "active")


def get_activate_menu(user_id: int, active: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅" if active else "❌",
                callback_data=active_menu_callback.new(
                    action="change_active",
                    user_id=user_id,
                    active="1" if active else "0"
                )
            )
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )