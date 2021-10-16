import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, User, ContentTypes

import keyboards
from filters import IsUser
from keyboards.default import trial
from loader import dp, scheduler, db
from states import Profile, Trial
from utils import show, send
from utils.db_api import redis_commands
from utils.misc import rate_limit


@rate_limit(1)
@dp.message_handler(IsUser(), CommandStart(), state="*")
async def bot_restart(msg: Message, state: FSMContext):
    user = User.get_current()

    await msg.answer("Мы тебя помним! Хочешь снова пообщаться с кем-то новым?",
                     reply_markup=keyboards.default.restart_btn)
    await msg.answer_sticker("CAACAgIAAxkBAAICdmFfXKTjierlUgNpIBZhmitf1GaHAAIxAAOymJoOP5HsZr15Gg0hBA")

    await state.finish()
    await Profile.activate_profile.set()

    logging.info(f"User @{user.username}-{user.id} restart bot")


@rate_limit(1)
@dp.message_handler(state=Profile.activate_profile, content_types=ContentTypes.ANY)
async def activate_profile(msg: Message, state: FSMContext):
    user = User.get_current()
    text = msg.text

    if text != "Начать 😎":
        await msg.answer("Нет такого варианта ответа")
        return

    user_data = await db.activate_user(user_id=user.id, active=not await redis_commands.is_ban(user.id))
    await redis_commands.activate_user(user_id=user.id)

    logging.info(f"User @{user.username}-{user.id} activate profile")

    await show.cur_user_profile(msg, state)
    await send.admin_info(user_data, is_registration=False)


@rate_limit(1)
@dp.message_handler(CommandStart(), state="*")
async def bot_start(msg: Message, state: FSMContext):
    user = msg.from_user

    await state.finish()

    scheduler.add_job(send_greeting, args=(msg, state))

    logging.info(f"User @{user.username}-{user.id} start bot")


async def send_greeting(msg: Message, state: FSMContext):
    user = msg.from_user

    await msg.answer("Привет, меня зовут Redfriend",
                     reply_markup=ReplyKeyboardRemove())
    await msg.answer_sticker("CAACAgIAAxkBAAEGriZhXYMJ5UGYhWje_rGtL6yM34HEXwACJQADspiaDg82d3yOk8EtIQQ")
    await asyncio.sleep(1)

    await msg.answer("Я буду находить для тебя лучших людей, с которыми можно погулять",
                     reply_markup=trial.how_work_btn)
    await msg.answer_sticker("CAACAgIAAxkBAAEGwJphZfMn7W6kreU0o97rV-9Cv1j9ggACHQADspiaDgrHcCVY8WNuIQQ")

    await Trial.how_work.set()

    logging.info(f"User @{user.username}-{user.id} got greeting")
