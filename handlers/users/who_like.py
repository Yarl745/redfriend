import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message

import keyboards
from loader import dp, db
from states import Likes
from utils import show, send, generate
from utils.db_api import redis_commands
from utils.misc import rate_limit


@dp.message_handler(state=Likes.show_likes, content_types=ContentTypes.ANY)
async def show_likes(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text

    if text != "Показать":
        await msg.answer("Нет такого варианта ответа")
        return

    logging.info(f"For User {user.username}-{user.id} start showing likes and matches")

    last_profile_id = (await state.get_data()).get("cur_profile_id")
    if last_profile_id:
        await redis_commands.set_last_profile_id(user_id=user.id, last_profile_id=last_profile_id)

    await Likes.get_like.set()
    await show.like(msg, state)


@rate_limit(0.5)
@dp.message_handler(text="👍", state=Likes.get_like)
async def match_profile(msg: Message, state: FSMContext):
    user = msg.from_user

    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} go to next like")

        await show.like(msg, state)
        return

    await state.reset_data()
    await db.match(from_user_id=cur_profile_id, to_user_id=user.id)

    user_data = await db.get_user(cur_profile_id)
    user_nick = user_data["user_nick"]
    await msg.answer("Отлично! Надеюсь хорошо проведёте время ;) "
                     "Начинай общаться 👉 {}".format(await generate.user_link(cur_profile_id, user_nick)),
                     disable_web_page_preview=True)

    likes_count = await redis_commands.add_match(from_user_id=user.id, to_user_id=cur_profile_id)

    await send.likes_info(cur_profile_id, likes_count)

    logging.info(f"User @{user.username}-{user.id} likes(match) profile of the User {cur_profile_id}")

    await show.like(msg, state)


@rate_limit(0.5)
@dp.message_handler(text="👎", state=Likes.get_like)
async def dismatch_profile(msg: Message, state: FSMContext):
    user = msg.from_user

    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} go to next like")

        await show.like(msg, state)
        return

    await state.reset_data()

    logging.info(f"User @{user.username}-{user.id} dislikes(not match) profile of the User {cur_profile_id}")

    await show.like(msg, state)


@rate_limit(0.5)
@dp.message_handler(state=Likes.get_like, content_types=ContentTypes.ANY)
async def default(msg: Message):
    user = msg.from_user

    await msg.answer("Нет такого варианта ответа ⤵️",
                     reply_markup=keyboards.default.match_menu)

    logging.info(f"User @{user.username}-{user.id} send undefined msg in like_menu(text={msg.text})")
