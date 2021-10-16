from data.config import ADMIN_CHAT_ID
from loader import bot
from utils import generate


async def block_info(**user_data):
    user_link = await generate.user_link(user_data["id"], user_data["user_nick"])

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text="Пользователь {} заблокировал бота".format(user_link)
    )
