import asyncio
import logging
import re

import emoji
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentTypes, User, CallbackQuery

import keyboards
from data.config import ANIMATION_MENU_ID, ANIMATION_KEYBOARD_ID, DEFAULT_PHOTO_ID
from keyboards.default import form
from keyboards.inline.register_btn import register_btn_callback
from loader import dp, db, scheduler
from states import UserForm, Search, Trial
from utils import generate, send, show
from utils.db_api import redis_commands


@dp.callback_query_handler(register_btn_callback.filter(), state=Trial.search_profiles)
async def start_registration(call: CallbackQuery, state: FSMContext):
    msg = call.message
    await msg.delete_reply_markup()
    scheduler.add_job(start_filling_form, args=(msg, state))


async def start_filling_form(msg: Message, state: FSMContext):
    user = msg.from_user

    await state.finish()

    await msg.answer("Давай определимся с полом",
                     reply_markup=form.sex_menu)
    await UserForm.enter_sex.set()

    await state.update_data(is_registration=True)

    logging.info(f"User @{user.username}-{user.id} started filling form")


async def restart_filling_form(msg: Message, state: FSMContext):
    user = User.get_current()

    user_data = await state.get_data()
    if not user_data or not user_data.get("user_nick", None):
        await state.finish()
        user_data.clear()

        db_user_data = await db.get_user(user.id)
        if db_user_data:
            user_data.update(
                description=db_user_data["description"],
                user_nick=db_user_data["user_nick"],
                media_id=db_user_data["media_id"],
                with_video=db_user_data["with_video"]
            )
            await state.update_data(
                **user_data
            )
            logging.info(f"Registered User @{user.username}-{user.id} start updating form")

    await msg.answer("Давай определимся с полом",
                     reply_markup=form.sex_menu)
    await UserForm.enter_sex.set()

    logging.info(f"User @{user.username}-{user.id} restarted filling form")


@dp.message_handler(state=UserForm.enter_sex, content_types=ContentTypes.ANY)
async def read_sex(msg: Message, state: FSMContext):
    user = msg.from_user
    sex = msg.text

    logging.info(f"User @{user.username}--{user.id} read sex({sex})")

    if sex != "Я девушка" and sex != "Я парень":
        await msg.answer(
            text="Давай определимся с полом",
            reply_markup=form.sex_menu
        )
        logging.info(f"User @{user.username}--{user.id} enter incorrect sex({sex})")
        return

    async with state.proxy() as data:
        data["sex"] = 1 if sex == "Я девушка" else 2

    await msg.answer(
        "Какие анкеты показывать?",
        reply_markup=form.search_menu
    )
    await UserForm.enter_search.set()


@dp.message_handler(state=UserForm.enter_search, content_types=ContentTypes.ANY)
async def read_search(msg: Message, state: FSMContext):
    user = msg.from_user
    search = msg.text

    logging.info(f"User @{user.username}--{user.id} read search({search})")

    if search != "Девушек" and search != "Парней" and search != "Всех всех":
        await msg.answer(
            text="Какие анкеты показывать?",
            reply_markup=form.search_menu
        )
        logging.info(f"User @{user.username}--{user.id} enter incorrect search({search})")
        return

    if search == "Девушек":
        search = 1
    elif search == "Парней":
        search = 2
    elif search == "Всех всех":
        search = 3

    await state.update_data(search=search)

    async with state.proxy() as data:
        data["search"] = search
        old_user_nick = data.get("user_nick", None)

    await msg.answer("Напиши, как мне тебя называть",
                     reply_markup=form.get_text_btn(text=old_user_nick) if old_user_nick else ReplyKeyboardRemove())
    await UserForm.enter_user_nick.set()


@dp.message_handler(state=UserForm.enter_user_nick, content_types=ContentTypes.ANY)
async def read_user_nick(msg: Message, state: FSMContext):
    user = msg.from_user
    user_nick = msg.text

    logging.info(f"User @{user.username}--{user.id} read user_nick({user_nick})")

    if not user_nick:
        await msg.answer("Напиши, как мне тебя называть")
        return

    user_nick = generate.clean_text(msg)

    async with state.proxy() as data:
        data["user_nick"] = user_nick
        old_description = data.get("description", None)

    await msg.answer(
        "Расскажи о себе, с кем хочешь погулять, чем предлагаешь заняться",
        reply_markup=form.get_text_btn("Оставить текущий текст", with_skip=True) if old_description else form.skip_btn
    )
    await msg.answer_sticker("CAACAgIAAxkBAAEGwNBhZhbjqVZnZPprd4irZaBkt1Af-wACKQADspiaDlxd6xJ1JVzHIQQ")
    await UserForm.enter_description.set()


# @dp.message_handler(state=UserForm.enter_relax, content_types=ContentTypes.ANY)
# async def read_relax(msg: Message, state: FSMContext):
#     user = msg.from_user
#     relax = msg.text
#
#     logging.info(f"User @{user.username}--{user.id} read relax(len={len(relax)})")
#
#     if not relax:
#         await msg.answer("Как хочешь провести свои выходные?")
#         return
#
#     async with state.proxy() as data:
#         if relax == "Пропустить":
#             data["relax"] = None
#         elif relax != "Оставить текущий текст":
#             relax = generate.clean_text(msg)
#             data["relax"] = relax[:250] if len(relax) > 250 else relax
#         old_joke = data.get("joke", None)
#
#     await msg.answer(
#         f"Что тебя веселит? Напиши пару примеров",
#         reply_markup=form.get_text_btn("Оставить текущий текст", with_skip=True) if old_joke else form.skip_btn
#     )
#     await msg.answer_sticker("CAACAgIAAxkBAAEGwGlhZer73fKTWF43A-iGXbuI9XiVAwACIAADspiaDmSLkRM19jGzIQQ")
#     await UserForm.enter_joke.set()
#
#
# @dp.message_handler(state=UserForm.enter_joke, content_types=ContentTypes.ANY)
# async def read_joke(msg: Message, state: FSMContext):
#     user = msg.from_user
#     joke = msg.text
#
#     logging.info(f"User @{user.username}--{user.id} read joke(len={len(joke)})")
#
#     if not joke:
#         await msg.answer("Что тебя веселит? Напиши пару примеров")
#         return
#
#     async with state.proxy() as data:
#         if joke == "Пропустить":
#             data["joke"] = None
#         elif joke != "Оставить текущий текст":
#             joke = generate.clean_text(msg)
#             data["joke"] = joke[:250] if len(joke) > 250 else joke
#         old_work = data.get("work", None)
#
#     await msg.answer(
#         "Кем хочешь стать, когда вырастешь?",
#         reply_markup=form.get_text_btn("Оставить текущий текст", with_skip=True) if old_work else form.skip_btn
#     )
#     await msg.answer_sticker("CAACAgIAAxkBAAEGwGxhZeuPwdaFHJVuGaifTlNORI9VMwACJgADspiaDjp5slwlaF5UIQQ")
#     await UserForm.enter_work.set()
#
#
# @dp.message_handler(state=UserForm.enter_work, content_types=ContentTypes.ANY)
# async def read_work(msg: Message, state: FSMContext):
#     user = msg.from_user
#     work = msg.text
#
#     logging.info(f"User @{user.username}--{user.id} read work(len={len(work)})")
#
#     if not work:
#         await msg.answer("Кем хочешь стать, когда вырастешь?")
#         return
#
#     async with state.proxy() as data:
#         if work == "Пропустить":
#             data["work"] = None
#         elif work != "Оставить текущий текст":
#             work = generate.clean_text(msg)
#             data["work"] = work[:250] if len(work) > 250 else work
#         old_media_id = data.get("media_id", None)
#
#     await msg.answer(
#         "Теперь пришли фото или запиши видео 👍 (до 15 сек), его будут видеть другие пользователи",
#         reply_markup=form.get_text_btn("Оставить текущее") if old_media_id else form.skip_btn
#     )
#     await msg.answer_sticker("CAACAgIAAxkBAAICcmFfWw2j22usE2zqHG3OOJMRqoLYAAIbAAOymJoOrpDCLTsVp5YhBA")
#     await UserForm.enter_media.set()


@dp.message_handler(state=UserForm.enter_description, content_types=ContentTypes.ANY)
async def read_description(msg: Message, state: FSMContext):
    user = msg.from_user
    description = msg.text

    logging.info(f"User @{user.username}--{user.id} read description({description})")

    if not description:
        await msg.answer("Расскажи о себе, с кем хочешь погулять, чем предлагаешь заняться")
        return

    async with state.proxy() as data:
        if description == "Пропустить":
            data["description"] = ""
        elif description != "Оставить текущий текст":
            description = generate.clean_text(msg)
            data["description"] = description[:600] if len(description) > 600 else description
        old_media_id = data.get("media_id", None)

    await msg.answer(
        "Теперь пришли фото или запиши видео 👍 (до 15 сек), его будут видеть другие пользователи",
        reply_markup=form.get_text_btn("Оставить текущее") if old_media_id else form.skip_btn
    )
    await msg.answer_sticker("CAACAgIAAxkBAAICcmFfWw2j22usE2zqHG3OOJMRqoLYAAIbAAOymJoOrpDCLTsVp5YhBA")
    await UserForm.enter_media.set()


@dp.message_handler(state=UserForm.enter_media, content_types=ContentTypes.ANY)
async def read_media(msg: Message, state: FSMContext):
    user = msg.from_user
    text = msg.text if msg.text == "Оставить текущее" or msg.text == "Пропустить" else None

    logging.info(f"User @{user.username}--{user.id} read photo")

    if not text and not msg.photo and not msg.video:
        await msg.answer("Нажми на кнопку скрепки и отправь своё фото или запиши видео 👍 (до 15 сек)")
        return

    if text == "Пропустить":
        user_photos = (await user.get_profile_photos(limit=1))["photos"]
        await state.update_data(
            media_id=user_photos[0][-1].file_id if user_photos else DEFAULT_PHOTO_ID,
            with_video=False
        )
    elif msg.photo:
        await state.update_data(
            media_id=msg.photo[-1].file_id,
            with_video=False
        )
    elif msg.video:
        if msg.video.duration > 15:
            await msg.reply("Видео должно длиться до 15 секунд, попробуй отправить другое")
            return
        await state.update_data(
            media_id=msg.video.file_id,
            with_video=True
        )

    user_data = await state.get_data()

    await msg.answer("Так выглядит твоя анкета:")
    await send.profile(to_chat_id=user.id, user_data=user_data)
    await msg.answer("Все верно?",
                     reply_markup=keyboards.default.form.confirm_menu)

    await UserForm.enter_confirm.set()


@dp.message_handler(state=UserForm.enter_confirm, content_types=ContentTypes.ANY)
async def read_confirm(msg: Message, state: FSMContext):
    user = msg.from_user
    confirm = msg.text

    logging.info(f"User @{user.username}--{user.id} read confirm({confirm})")

    if confirm != "Да" and confirm != "Изменить анкету":
        await msg.answer(
            text="Нет такого варианта ответа ⤵️",
            reply_markup=keyboards.default.form.confirm_menu
        )
        logging.info(f"User @{user.username}--{user.id} enter incorrect confirm({confirm})")
        return

    if confirm == "Да":
        scheduler.add_job(finish_filling_form, args=(msg, state,))
    elif confirm == "Изменить анкету":
        await restart_filling_form(msg, state)


async def finish_filling_form(msg: Message, state: FSMContext):
    user = User.get_current()
    user_data = await state.get_data()
    is_registration = user_data.pop("is_registration", False)

    user_data.update(
        id=user.id,
        username=user.username if user.username else ""
    )

    is_updated = await db.update_user(
        user_id=user.id,
        **user_data
    )

    if not is_updated:
        await db.add_user(
            **user_data
        )
        await redis_commands.activate_user(user_id=user.id)

    await redis_commands.clear_search_ids(for_user_id=user.id)
    await state.finish()

    await send.admin_info(user_data, is_registration=is_registration)

    if is_registration:
        await msg.answer_animation(
            animation=ANIMATION_MENU_ID,
            caption="Жми эту кнопку, чтобы открыть меню",
            reply_markup=ReplyKeyboardRemove()
        )
        await asyncio.sleep(3)

    logging.info(f"User @{user.username}-{user.id} finish filling form")

    await Search.searching_profiles.set()
    await show.random_profile(msg, state, update_keyboard=True)
