import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import User

import keyboards
from loader import db, bot
from states import Profile
from utils import send, generate
from utils.db_api import redis_commands


async def user_profile(user_id: int, to_chat_id: int, state: FSMContext, keyboard=None,
                       like_msg_text=None, is_match=False):
    to_chat_user = User.get_current()
    user_data = await db.get_user(user_id)

    if is_match:
        user_nick = user_data["user_nick"]
        await bot.send_message(
            chat_id=to_chat_id,
            text="Начинай общаться 👉 {}".format(await generate.user_link(user_id, user_nick)),
            disable_web_page_preview=True
        )

    await send.profile(to_chat_id=to_chat_id,
                       user_data=user_data,
                       keyboard=keyboard,
                       like_msg_text=like_msg_text)

    await state.update_data(cur_profile_id=user_id)

    logging.info(f"For User @{to_chat_user.username}-{to_chat_user.id} show current profile "
                 f"of the @{user_data['username']}-{user_data['id']}")
