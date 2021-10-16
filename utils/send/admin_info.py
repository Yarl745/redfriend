import keyboards
from data.config import ADMIN_CHAT_ID
from utils import send, generate
from utils.db_api import redis_commands


async def admin_info(user_data: dict, is_registration=False):
    user_id = user_data["id"]
    user_nick = user_data["user_nick"]
    sex = user_data["sex"]
    search = user_data["search"]

    user_link = await generate.user_link(user_id, user_nick)
    if is_registration:
        info_text = "{} зарегестрировался\n[{} -> {}]\n\n<code>{}</code>".format(user_link, sex, search, user_id)
    else:
        info_text = "{} обновил профиль\n[{} -> {}]\n\n<code>{}</code>".format(user_link, sex, search, user_id)

    is_ban = await redis_commands.is_ban(user_data["id"])

    await send.profile(
        to_chat_id=ADMIN_CHAT_ID,
        user_data=user_data,
        like_msg_text=info_text,
        keyboard=keyboards.inline.get_activate_menu(user_id=user_id, active=not is_ban)
    )
