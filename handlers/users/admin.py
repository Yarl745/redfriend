import asyncio
import logging
import random

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message, CallbackQuery
from aiogram.utils.exceptions import BotBlocked

import keyboards
from data.config import ADMINS, ADMIN_CHAT_ID
from keyboards.inline.activate_menu import active_menu_callback
from loader import dp, db, storage
from utils import text
from utils.db_api import redis_commands
from utils.jobs import cur_bot_info
from utils.misc import rate_limit


@dp.message_handler(commands="upload", user_id=ADMINS, state="*")
async def upload_profile(command_msg: Message, state: FSMContext):
    profile_msg = command_msg.reply_to_message
    admin = command_msg.from_user
    param = command_msg.get_args()

    if not profile_msg:
        await command_msg.answer("Чтобы загрузить анкету сделай на неё REPLY")
        return
    elif param != "g" and param != "b":
        await command_msg.answer("Чтобы воспользоваться командой /upload нужно добавить параметры <b>b | g</b>")
        return

    other_bot = profile_msg.forward_from
    if not other_bot or other_bot.id != 1234060895:
        await profile_msg.reply("Загружать анкеты можно только из нашего БотаX :)")
        return
    elif (not profile_msg.photo and not profile_msg.video) or not profile_msg.caption:
        await profile_msg.reply("Загружать нужно именно анкету, а не части анкеты")
        return

    profile_data = text.get_parse_data(profile_msg.caption)
    if profile_msg.photo:
        media_id = profile_msg.photo[-1].file_id
        with_video = False
    else:
        media_id = profile_msg.video.file_id
        with_video = True

    profile_data.update(
        id=random.randint(1, 100000),
        username="f",
        media_id=media_id,
        with_video=with_video,
        sex=1 if param == "g" else 2
    )

    await db.add_user(**profile_data)
    await profile_msg.reply("Пользователь {}-{} успешно добавлен ✅"
                            "".format(profile_data["user_nick"], profile_data["id"]))
    logging.info(f"Admin @{admin.username}-{admin.id} successfully "
                 f"added fake {profile_data['user_nick']}-{profile_data['id']} ")


@dp.message_handler(commands="get_msg_info", user_id=ADMINS, state="*")
async def get_msg_info(command_msg: Message, state: FSMContext):
    msg = command_msg.reply_to_message

    await command_msg.delete()

    if not msg:
        await command_msg.answer("Нужно делать реплай на сообщение.")
        return

    state = await state.get_state()
    await msg.reply(f"Эхо в состоянии <code>{state}</code>.\n"
                    f"\nСодержание сообщения:\n"
                    f"\n<code>{msg}</code>\n"
                    f"\ncontent_type = {msg.content_type}\n"
                    f"\nentities={msg.entities}")


@dp.message_handler(commands="ban_user", user_id=ADMINS, state="*")
async def ban_user(command_msg: Message, state: FSMContext):
    ban_user_id = command_msg.get_args()
    admin = command_msg.from_user

    await command_msg.delete()

    if not ban_user_id or not ban_user_id.isdecimal():
        await command_msg.answer(f"Формат команды: /ban_user user_id")
        return
    ban_user_id = int(ban_user_id)

    is_banned = await db.ban_user(ban_user_id)
    if not is_banned:
        await command_msg.answer(f"Пользователя с таким <user_id> не существует")
        return

    await redis_commands.ban_user(ban_user_id)

    await command_msg.answer("Пользователь({}) успешно забанен 😎".format(ban_user_id))

    logging.info(f"Admin @{admin.username}-{admin.id} BAN USER-{ban_user_id}")


@dp.message_handler(commands="unban_user", user_id=ADMINS, state="*")
async def unban_user(command_msg: Message, state: FSMContext):
    unban_user_id = command_msg.get_args()
    admin = command_msg.from_user

    await command_msg.delete()

    if not unban_user_id or not unban_user_id.isdecimal():
        await command_msg.answer(f"Формат команды: /unban_user user_id")
        return
    unban_user_id = int(unban_user_id)

    is_unbanned = await db.unban_user(unban_user_id)
    if not is_unbanned:
        await command_msg.answer(f"Пользователя с таким <user_id> не существует")
        return

    await redis_commands.unban_user(unban_user_id)

    await command_msg.answer("Пользователь({}) успешно разбанен 👻".format(unban_user_id))

    logging.info(f"Admin @{admin.username}-{admin.id} UNBAN USER-{unban_user_id}")


@dp.message_handler(commands="clean_old_likes", user_id=ADMINS, state="*")
async def clean_old_likes(command_msg: Message, state: FSMContext):
    admin = command_msg.from_user

    await command_msg.delete()

    count = await db.clean_old_likes(interval=24)

    await command_msg.answer("Было успешно удалено {} старых лайков(за {} hours)".format(count, 24))

    logging.info(f"Admin @{admin.username}-{admin.id} delete old likes(count={count})")


@dp.message_handler(commands="say_to_all_now_go", user_id=ADMINS, state="*")
async def say_to_all(command_msg: Message, state: FSMContext):
    admin = command_msg.from_user
    msg = command_msg.reply_to_message

    await command_msg.delete()

    if not msg:
        await command_msg.answer("Чтобы воспользоваться этой командой сделай REPLY")
        return

    active_user_ids = await db.get_all_users(active=True)  # [375766905, 997319478]
    delete_bot_count = 0

    for user_id in active_user_ids:
        try:
            await dp.bot.copy_message(
                chat_id=user_id,
                from_chat_id=command_msg.chat.id,
                message_id=msg.message_id
            )
            await asyncio.sleep(0.05)
        except BotBlocked as exc:
            await db.update_user(user_id, active=False)
            await redis_commands.clear_user(user_id)
            await redis_commands.clear_search_ids(user_id)
            delete_bot_count += 1

    await msg.reply("Сообщение успешно отправлено: оставили бот({}), заблокировали бот({})"
                    "".format(len(active_user_ids) - delete_bot_count, delete_bot_count))

    logging.info(f"Admin @{admin.username}-{admin.id} SAY TO ALL MSG(id={msg.message_id})")


@dp.message_handler(commands="show_state_statistic", user_id=ADMINS, state="*")
async def show_state_statistic(command_msg: Message, state: FSMContext):
    admin = command_msg.from_user
    statistic = dict()

    await command_msg.delete()

    states_list = await storage.get_states_list()
    for states_item in states_list:
        chat_id, user_id = states_item
        state_text = await storage.get_state(chat=chat_id, user=user_id, default="Deactivate bot")
        try:
            statistic[state_text] += 1
        except KeyError:
            statistic.update({state_text: 1})

    out_text = "<b>Статичктика по пользователям:</b>\n\n"
    for state_text, count_users in statistic.items():
        out_text += f"В состоянии {state_text} — {count_users} пользователей\n\n"

    await command_msg.answer(out_text)

    logging.info(f"For Admin @{admin.username}-{admin.id} show state statistic")


@rate_limit(3)
@dp.message_handler(commands="show_info", user_id=ADMINS, state="*")
async def show_info(command_msg: Message, state: FSMContext):
    admin = command_msg.from_user

    await command_msg.delete()

    await cur_bot_info(for_chat_id=command_msg.chat.id)

    logging.info(f"For admin @{admin.username}-{admin.id} SHOW INFO(command)")


@dp.callback_query_handler(active_menu_callback.filter(), chat_id=ADMIN_CHAT_ID, state="*")
async def change_active(call: CallbackQuery, state: FSMContext, callback_data: dict):
    active = not bool(int(callback_data["active"]))
    user_id = int(callback_data["user_id"])
    admin = call.from_user
    profile_msg = call.message

    if active:
        await db.unban_user(user_id)
        await redis_commands.unban_user(user_id)
    else:
        await db.ban_user(user_id)
        await redis_commands.ban_user(user_id)

    await profile_msg.edit_reply_markup(keyboards.inline.get_activate_menu(user_id=user_id, active=active))
    await call.answer()

    logging.info(f"Admin @{admin.username}-{admin.id} CHANGE ACTIVE FOR USER-{user_id} TO {active}")
