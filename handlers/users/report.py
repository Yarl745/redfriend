import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from data.config import REPORTS_CHAT_ID
from keyboards.inline.report_menu import report_menu_callback
from loader import dp, db
from utils import show


@dp.callback_query_handler(report_menu_callback.filter(), state="*")
async def send_report(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user = call.from_user
    report_user_id = int(callback_data["user_id"])
    action = callback_data["action"]
    msg = call.message

    await msg.delete_reply_markup()

    if action == "cancel":
        logging.info(f"User @{user.username}-{user.id} CANCELED REPORT User-{report_user_id}")
        return

    cause = "Жалоба: "
    if action == "adult_content":
        cause += "Материал для взрослых🔞"
    elif action == "sale_content":
        cause += "Продажа товаров и услуг💰"
    elif action == "other_content":
        cause += "Другое🦨"
    cause += f" от {user.get_mention()}\n\n<code>{report_user_id}</code>"

    await call.answer(
        text="Спасибо тебе за то, что помогаешь делать бот лучше 😇",
        show_alert=True
    )

    is_added = await db.add_report(from_user_id=user.id, to_user_id=report_user_id, cause=action)
    if not is_added:
        logging.info(f"User @{user.username}-{user.id} ALREADY REPORTED User-{report_user_id}({action})")
        return

    await show.user_profile(report_user_id, to_chat_id=REPORTS_CHAT_ID, state=state,
                            like_msg_text=cause, is_match=True)
    logging.info(f"User @{user.username}-{user.id} REPORT User-{report_user_id}({action})")




