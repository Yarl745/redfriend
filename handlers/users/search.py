import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message

import keyboards
from loader import dp, db
from states import Profile, Search
from utils import send, show, generate
from utils.db_api import redis_commands
from utils.misc import rate_limit


@dp.message_handler(state=Profile.profile_action, content_types=ContentTypes.ANY)
async def search_profiles(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text

    if text != "Смотреть анкеты":
        await msg.answer("Нет такого варианта ответа")
        return

    await state.finish()
    await Search.searching_profiles.set()

    last_profile_id = await redis_commands.del_last_profile_id(user.id)
    if last_profile_id:
        await show.user_profile(user_id=last_profile_id, to_chat_id=user.id,
                                state=state, keyboard=keyboards.default.like_menu)
        logging.info(f"User @{user.username}-{user.id} start searching profiles(with last profile id({last_profile_id}))")
        return

    logging.info(f"User @{user.username}-{user.id} start searching profiles")

    await show.random_profile(msg, state, update_keyboard=True)


@rate_limit(0.5)
@dp.message_handler(text="👍", state=Search.searching_profiles)
async def like_profile(msg: Message, state: FSMContext):
    user = msg.from_user

    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state)
        return

    if await redis_commands.is_ban(user.id):
        logging.info(f"User @{user.username}-{user.id} in BAN (only showing)")

        await show.random_profile(msg, state)
        return

    is_added = await db.add_like(from_user_id=user.id, to_user_id=cur_profile_id)
    if not is_added:
        logging.info(f"User @{user.username}-{user.id} already is liked profile of the User {cur_profile_id}")
        await show.random_profile(msg, state)
        return

    likes_count = await redis_commands.add_like(from_user_id=user.id, to_user_id=cur_profile_id)

    await send.likes_info(cur_profile_id, likes_count)

    logging.info(f"User @{user.username}-{user.id} likes profile of the User {cur_profile_id}")

    await show.random_profile(msg, state)


@rate_limit(0.5)
@dp.message_handler(text="👎", state=Search.searching_profiles)
async def dislike_profile(msg: Message, state: FSMContext):
    user = msg.from_user
    user_data = await state.get_data()
    cur_profile_id = user_data.get("cur_profile_id")

    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state)
        return

    logging.info(f"User @{user.username}-{user.id} dislikes profile of the User {cur_profile_id}")

    await show.random_profile(msg, state)


@rate_limit(0.5)
@dp.message_handler(text="💌", state=Search.searching_profiles)
async def write_love_msg(msg: Message, state: FSMContext):
    user = msg.from_user
    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state)
        return

    await Search.write_love_msg.set()
    await msg.answer("Напиши сообщение для этого пользователя",
                     reply_markup=keyboards.default.back_btn)

    logging.info(f"User @{user.username}-{user.id} want to write love msg to User-{user.id}")


@dp.message_handler(state=Search.write_love_msg, content_types=ContentTypes.ANY)
async def send_love_msg(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text
    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state)
        return

    if not text:
        await msg.answer("Напиши сообщение для этого пользователя",
                         reply_markup=keyboards.default.back_btn)
        return
    elif text == "Вернуться назад":
        await Search.searching_profiles.set()
        await show.user_profile(user_id=cur_profile_id, to_chat_id=user.id,
                                state=state, keyboard=keyboards.default.like_menu)
        logging.info(f"User @{user.username}-{user.id} canceled sending love msg for User-{cur_profile_id}")
        return
    text = generate.clean_text(msg)
    text = text[:250] if len(text) > 250 else text

    # Back to search
    await Search.searching_profiles.set()

    if await redis_commands.is_ban(user.id):
        logging.info(f"User @{user.username}-{user.id} in BAN (only showing)")
        await show.random_profile(msg, state, update_keyboard=True)
        return

    is_added = await db.add_like(from_user_id=user.id, to_user_id=cur_profile_id)
    if not is_added:
        logging.info(f"User @{user.username}-{user.id} already is liked profile of the User {cur_profile_id}")
        await show.random_profile(msg, state, update_keyboard=True)
        return

    likes_count = await redis_commands.add_like(from_user_id=user.id, to_user_id=cur_profile_id, with_msg=True)
    await redis_commands.add_love_msg(from_user_id=user.id, to_user_id=cur_profile_id, msg_text=text)

    await send.likes_info(cur_profile_id, likes_count)

    logging.info(f"User @{user.username}-{user.id} send love msg to User {cur_profile_id} length({len(text)})")

    await show.random_profile(msg, state, update_keyboard=True)


@rate_limit(0.5)
@dp.message_handler(state=Search.searching_profiles, content_types=ContentTypes.ANY)
async def default(msg: Message):
    user = msg.from_user

    await msg.reply(text="Нет такого варианта ответа ⤵️",
                    reply_markup=keyboards.default.like_menu)

    logging.info(f"User @{user.username}-{user.id} send undefined msg in search(text={msg.text})")