import logging

from aiogram.utils.exceptions import BotBlocked

import keyboards
from loader import bot, storage, db
from states import Likes
from utils import send
from utils.db_api import redis_commands


async def likes_info(for_user_id: int, likes_count: int):
    # user_cache = await db.get_user_cache(for_user_id)
    # search = int(user_cache.get(b'search', 0))
    # sex = int(user_cache.get(b'sex', 0))

    if not await redis_commands.is_active(for_user_id):
        logging.info(f"User {for_user_id} can't get likes NOT ACTIVE profile")
        return

    if likes_count not in (1, 2, 5, 7, 10, 20, 30, 50, 100):
        logging.info(f"Many likes for User-{for_user_id}(count={likes_count})")
        return

    if likes_count > 2:
        text = "{} человек хотят с тобой погулять, показать их?".format(likes_count)
    elif likes_count == 2:
        text = "2 человека хотят с тобой погулять, показать их?"
    else:
        text = "Кто-то хочет с тобой погулять, показать его?"

    try:
        await bot.send_message(
            chat_id=for_user_id,
            text=text,
            reply_markup=keyboards.default.show_likes_btn
        )
    except BotBlocked as exc:
        await db.update_user(for_user_id, active=False)
        await redis_commands.clear_user(for_user_id)
        await redis_commands.clear_search_ids(for_user_id)
        await send.block_info(id=for_user_id, user_nick=(await db.get_cache(for_user_id))["user_nick"])

    # state = FSMContext(storage=storage, chat=user_id, user=user_id)
    # await state.set_state(state=Search.show_likes.stat)
    await storage.set_state(chat=for_user_id, user=for_user_id, state=Likes.show_likes.state)

    logging.info(f"Send likes info for User {for_user_id}")