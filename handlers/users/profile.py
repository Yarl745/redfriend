import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, User, CallbackQuery, ContentTypes

import keyboards
from handlers.users.fill_form import restart_filling_form
from keyboards.inline.profile_menu import profile_menu_callback
from loader import dp, db
from states import Profile
from utils import show
from utils.db_api import redis_commands


@dp.callback_query_handler(profile_menu_callback.filter(action="change_profile"), state=Profile.profile_action)
async def change_profile(call: CallbackQuery, state: FSMContext):
    user = call.from_user
    msg = call.message

    await restart_filling_form(msg, state)

    await msg.delete_reply_markup()


@dp.callback_query_handler(profile_menu_callback.filter(action="disable_profile"), state=Profile.profile_action)
async def want_disable_profile(call: CallbackQuery, state: FSMContext):
    user = call.from_user
    msg = call.message

    await msg.answer("Так ты не узнаешь, что кто-то хочет погулять с тобой... Точно хочешь отключить свою анкету?",
                     reply_markup=keyboards.default.disable_menu)

    await Profile.disable_profile.set()

    await msg.delete_reply_markup()

    logging.info(f"User @{user.username}-{user.id} want disable profile")


@dp.message_handler(state=Profile.disable_profile, content_types=ContentTypes.ANY)
async def disable_profile(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text

    if text != "Да, отключить анкету" and text != "Нет, вернуться назад":
        await msg.answer("Нет такого варианта ответа")
        return

    if text == "Нет, вернуться назад":
        await show.cur_user_profile(msg, state)
    elif text == "Да, отключить анкету":
        await db.update_user(user.id, active=False)
        await redis_commands.clear_user(user.id)
        await redis_commands.clear_search_ids(user.id)
        await msg.answer("Надеюсь ты нашел кого-то благодаря мне! Рад был с тобой пообщаться, "
                         "будет скучно — пиши, обязательно найдём тебе кого-нибудь",
                         reply_markup=keyboards.default.search_btn)
        await msg.answer_sticker("CAACAgIAAxkBAAIDjGFgHp01Mt0GzXv8AAGB4m1N8v99zAACHQADspiaDgrHcCVY8WNuIQQ")
        await state.finish()

    logging.info(f"User @{user.username}-{user.id} disable profile({text})")





