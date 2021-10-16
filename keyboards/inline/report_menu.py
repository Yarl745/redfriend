from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


report_menu_callback = CallbackData("report_menu", "action", "user_id")


def get_report_menu(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton(
                "🔞 Материал для взрослых", callback_data=report_menu_callback.new(
                    action="adult_content",
                    user_id=user_id
                )
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Продажа товаров и услуг", callback_data=report_menu_callback.new(
                    action="sale_content",
                    user_id=user_id
                )
            )
        ],
        [
            InlineKeyboardButton(
                "🦨 Другое", callback_data=report_menu_callback.new(
                    action="other_content",
                    user_id=user_id
                )
            )
        ],
        [
            InlineKeyboardButton(
                "✖️ Отмена", callback_data=report_menu_callback.new(
                    action="cancel",
                    user_id=user_id
                )
            )
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )