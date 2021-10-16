from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from loader import dp
import logging


@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def default_msg(msg: types.Message, state: FSMContext):
    user = msg.from_user
    state = await state.get_state()

    if user.is_bot:
        return

    await msg.answer("Для того чтобы снова пользоваться ботом нажми на 👉 /start")
    logging.info(f"User @{user.username}-{user.id} in {state} state - suggest /start")


@dp.callback_query_handler(state="*")
async def default_msg(call: CallbackQuery, state: FSMContext):
    user = call.from_user
    state = await state.get_state()
    msg = call.message

    await msg.answer("Для того чтобы снова пользоваться ботом нажми на 👉 /start")
    await call.answer()
    logging.info(f"User @{user.username}-{user.id} in {state} state - suggest /start")
