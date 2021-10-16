import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message, ReplyKeyboardRemove

import keyboards
from data.config import ANIMATION_KEYBOARD_ID
from keyboards.default import trial
from loader import dp
from states import Trial
from utils import show, send
from utils.db_api import redis_commands
from utils.misc import rate_limit


@dp.message_handler(state=Trial.how_work, content_types=ContentTypes.ANY)
async def how_work(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text

    if not text or text != "Как ты работаешь? 🤔":
        await msg.reply(text="Нет такого варианта ответа ⤵️",
                        reply_markup=trial.how_work_btn)
        return

    await msg.answer("Всё просто! У каждого студента есть своя анкета\n\n"
                     "Если нашёл интересного человека, то лайкаешь его анкету и вы начинаете общаться 👍",
                     reply_markup=trial.show_profiles_btn)
    await msg.answer_sticker("CAACAgIAAxkBAAEGwKFhZfNQ8rIU8vf0_SEWwX2y_9Fz6QACGQADspiaDkQHunBK4gPsIQQ")

    await Trial.show_profiles.set()

    logging.info(f"For User @{user.username}-{user.id} send how bot works")


@dp.message_handler(state=Trial.show_profiles, content_types=ContentTypes.ANY)
async def search_profiles(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text

    if text != "Посмотреть анкеты 👀":
        await msg.reply(text="Нет такого варианта ответа ⤵️",
                        reply_markup=trial.show_profiles_btn)
        return

    await state.finish()
    await Trial.search_profiles.set()

    logging.info(f"User @{user.username}-{user.id} start searching profiles")

    await show.random_profile(msg, state, update_keyboard=True)
    await send.suggest_register(msg)


@rate_limit(0.7)
@dp.message_handler(text="👍", state=Trial.search_profiles)
async def like_profile(msg: Message, state: FSMContext):
    user = msg.from_user

    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"NOT ACTIVE User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state, update_keyboard=True)
        return

    logging.info(f"NOT ACTIVE User @{user.username}-{user.id} try to like profile of the User {cur_profile_id}")

    await show.random_profile(msg, state)
    await send.suggest_register(msg)


@rate_limit(0.5)
@dp.message_handler(text="👎", state=Trial.search_profiles)
async def dislike_profile(msg: Message, state: FSMContext):
    user = msg.from_user
    user_data = await state.get_data()
    cur_profile_id = user_data.get("cur_profile_id")

    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"NOT ACTIVE User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state, update_keyboard=True)
        return

    logging.info(f"NOT ACTIVE User @{user.username}-{user.id} try to dislike profile of the User {cur_profile_id}")

    await show.random_profile(msg, state)


@rate_limit(0.7)
@dp.message_handler(text="💌", state=Trial.search_profiles)
async def write_love_msg(msg: Message, state: FSMContext):
    user = msg.from_user
    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"NOT ACTIVE User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state, update_keyboard=True)
        return

    await Trial.write_love_msg.set()
    await msg.answer("Напиши сообщение для этого пользователя",
                     reply_markup=keyboards.default.back_btn)

    logging.info(f"NOT ACTIVE User @{user.username}-{user.id} want to write love msg to User-{user.id}")


@dp.message_handler(state=Trial.write_love_msg, content_types=ContentTypes.ANY)
async def send_love_msg(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text
    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await state.reset_data()

        logging.info(f"User @{user.username}-{user.id} start searching profiles")

        await show.random_profile(msg, state, update_keyboard=True)
        return

    if not text:
        await msg.answer("Напиши сообщение для этого пользователя",
                         reply_markup=keyboards.default.back_btn)
        return
    elif text == "Вернуться назад":
        await Trial.search_profiles.set()
        await show.user_profile(user_id=cur_profile_id, to_chat_id=user.id,
                                state=state, keyboard=keyboards.default.like_menu)
        logging.info(f"NOT ACTIVE User @{user.username}-{user.id} canceled sending love msg for User-{cur_profile_id}")
        return

    # Back to search
    await Trial.search_profiles.set()

    logging.info(f"NOT ACTIVE User @{user.username}-{user.id} try to send love msg to User {cur_profile_id} length({len(text)})")

    await show.random_profile(msg, state, update_keyboard=True)
    await send.suggest_register(msg)


@rate_limit(0.8)
@dp.message_handler(state=Trial.search_profiles, content_types=ContentTypes.ANY)
async def default(msg: Message):
    user = msg.from_user

    await msg.reply(text="Нет такого варианта ответа ⤵️",
                    reply_markup=keyboards.default.like_menu)

    logging.info(f"NOT ACTIVE User @{user.username}-{user.id} send undefined msg in search(text={msg.text})")


