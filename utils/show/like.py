import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import keyboards
from loader import scheduler
from utils import show
from utils.db_api import redis_commands


async def like(msg: Message, state: FSMContext):
    user = msg.from_user

    last_data = await state.get_data()
    like_user_id = last_data.get("like_user_id", None)
    like_msg_text = last_data.get("like_msg_text", None)

    # Если не определился с последним провелем и залетел новый лайк
    if not like_user_id:
        like_user_id, like_msg_text = await redis_commands.get_like(user.id)

    while like_user_id and await redis_commands.is_ban(like_user_id):
        like_user_id, like_msg_text = await redis_commands.get_like(user.id)

    await state.update_data(
        like_user_id=like_user_id,
        like_msg_text=like_msg_text
    )

    if not like_user_id:
        await state.reset_data()
        scheduler.add_job(show.matches, args=(msg, state,))
        return

    await show.user_profile(like_user_id, to_chat_id=user.id, state=state,
                            keyboard=keyboards.default.match_menu, like_msg_text=like_msg_text)

    logging.info(f"For User @{user.username}-{user.id} show like of the User-{like_user_id}")
