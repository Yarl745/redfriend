import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import keyboards
from states import Profile
from utils import show
from utils.db_api import redis_commands


async def matches(msg: Message, state: FSMContext):
    user = msg.from_user

    match_user_ids = await redis_commands.get_matches(for_user_id=user.id)

    for match_user_id in match_user_ids:
        await show.user_profile(user_id=match_user_id, to_chat_id=user.id, state=state, is_match=True)
        await asyncio.sleep(0.15)

    await msg.answer("Это всё, идём дальше?", reply_markup=keyboards.default.search_btn)
    await Profile.profile_action.set()

    logging.info(f"For User @{user.username}-{user.id} showed all matches(count={len(match_user_ids)})")