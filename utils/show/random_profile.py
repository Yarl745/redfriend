import logging

import keyboards
from loader import db
from states import Profile
from utils import send
from utils.db_api import redis_commands


async def random_profile(msg, state, update_keyboard=False):
    user = msg.from_user
    search_user_id = await redis_commands.get_search_id(user.id)
    while search_user_id and await redis_commands.is_ban(search_user_id):
        search_user_id = await redis_commands.get_search_id(user.id)

    if not search_user_id:
        last_search_ids = await redis_commands.get_last_search_ids(user.id)
        user_cache = await db.get_cache(user.id)
        random_search_ids = await db.get_random_search_ids(last_search_ids, search=user_cache["search"] if user_cache else 3)
        if random_search_ids:
            search_user_id = random_search_ids.pop()
            await redis_commands.update_search_ids(for_user_id=user.id, search_ids=random_search_ids)

    rand_user = await db.get_user(search_user_id) if search_user_id else None

    if not rand_user:
        await msg.answer("Сейчас активных анкет нету, но подожди чуть-чуть "
                         "и уже сегодня здесь появится куча крутых людей",
                         reply_markup=keyboards.default.search_btn)
        await msg.answer_sticker("CAACAgIAAxkBAAEGrvZhXfwhQgNf1vOpKtvLww_UksmD9QACLQADspiaDjNDDBN84xWVIQQ")
        await Profile.profile_action.set()
        logging.info(f"For User @{user.username}-{user.id} not exists active profiles")
        return

    await send.profile(to_chat_id=user.id,
                       user_data=rand_user,
                       keyboard=keyboards.default.like_menu if update_keyboard else None)

    await state.update_data(cur_profile_id=rand_user["id"])

    logging.info(f"For User @{user.username}-{user.id} show random profile "
                 f"of the @{rand_user['username']}-{rand_user['id']}")
