import logging

from aiogram.types import User

from data import config
from loader import bot
from utils import generate


async def profile(to_chat_id: int, user_data: dict, keyboard=None, like_msg_text: str = None):
    user = User.get_current()
    profile_text = generate.profile_text(user_data)
    like_msg = "Сообщение для тебя💌: {}".format(like_msg_text)
    profile_text = f"{profile_text}{like_msg if like_msg_text else ''}"
    media_id = user_data.get("media_id", config.DEFAULT_PHOTO)
    with_video = user_data.get("with_video", False)

    if with_video:
        await bot.send_video(
            chat_id=to_chat_id,
            video=media_id,
            caption=profile_text,
            reply_markup=keyboard
        )
    else:
        await bot.send_photo(
            chat_id=to_chat_id,
            photo=media_id,
            caption=profile_text,
            reply_markup=keyboard
        )

    logging.info(f"Send profile for User @{user.username}-{user.id}")