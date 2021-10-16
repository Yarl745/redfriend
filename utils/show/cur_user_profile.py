import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, User

import keyboards
from loader import db
from states import Profile
from utils import send


async def cur_user_profile(msg: Message, state: FSMContext):
    user = User.get_current()

    user_data = await db.get_user(user.id)

    await msg.answer("Так выглядит твоя анкета:", reply_markup=keyboards.default.search_btn)
    await send.profile(to_chat_id=user.id, user_data=user_data, keyboard=keyboards.inline.get_profile_menu(user.id))

    await Profile.profile_action.set()

    logging.info(f"For @{user.username}-{user.id} show profile")