import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

import keyboards
from data.config import ANIMATION_KEYBOARD_ID
from filters import IsActive, IsUser
from loader import dp
from states import Search, Trial
from utils import show


@dp.message_handler(IsActive(), commands="myprofile", state="*")
async def get_profile(msg: Message, state: FSMContext):
    user = msg.from_user
    user.get_mention()
    logging.info(f"User @{user.username}-{user.id} enter /myprofile")

    await state.finish()

    await show.cur_user_profile(msg, state)


@dp.message_handler(IsActive(), commands="search", state="*")
async def search_profiles(msg: Message, state: FSMContext):
    user = msg.from_user

    await state.finish()
    await Search.searching_profiles.set()

    logging.info(f"User @{user.username}-{user.id} enter /search")

    await show.random_profile(msg, state, update_keyboard=True)


@dp.message_handler(IsActive(), commands="report", state="*")
async def report_profile(msg: Message, state: FSMContext):
    user = msg.from_user

    cur_profile_id = (await state.get_data()).get("cur_profile_id")
    if not cur_profile_id:
        await msg.answer("Жалобу можно оставить только при просмотре анкеты")
        logging.info(f"User @{user.username}-{user.id} REPORT without profile")
        return

    await show.user_profile(cur_profile_id, to_chat_id=user.id, state=state,
                            keyboard=keyboards.inline.get_report_menu(cur_profile_id))

    logging.info(f"User @{user.username}-{user.id} want /report User-{cur_profile_id}")


@dp.message_handler(Command(["myprofile", "search", "report"]), ~IsUser(), state=Trial.search_profiles)
async def not_registered(command_msg: Message):
    await command_msg.delete()

    await command_msg.answer("Чтобы пользоваться меню, необходимо заполнить небольшую анкету",
                             reply_markup=keyboards.inline.register_btn)


@dp.message_handler(Command(["myprofile", "search", "report"]), ~IsUser(), state="*")
async def not_trial(command_msg: Message):
    user = command_msg.from_user

    await command_msg.delete()

    await command_msg.answer_animation(
        animation=ANIMATION_KEYBOARD_ID,
        caption="Если не можешь найти, куда жать, то жми на эту кнопку"
    )

    logging.info(f"User @{user.username}-{user.id} CAN'T FIND BUTTONS")
