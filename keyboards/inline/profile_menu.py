from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

profile_menu_callback = CallbackData("profile_menu", "action", "user_id")


def get_profile_menu(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton(
                "✨ Изменить анкету ✨", callback_data=profile_menu_callback.new(
                    action="change_profile",
                    user_id=user_id
                )
            )
        ],
        [
            InlineKeyboardButton(
                "Отключить анкету", callback_data=profile_menu_callback.new(
                    action="disable_profile",
                    user_id=user_id
                )
            )
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )