from data.config import ERRORS_CHAT_ID
from loader import bot
import logging


async def exception(update=None, exc=None):
    await bot.send_message(
        ERRORS_CHAT_ID,
        text="<b>Update:</b>\n"
             "<code>{update}</code>\n\n\n"
             "<b>Exception:</b>\n"
             "<code>{exc}</code>"
             "".format(update=update, exc=exc)
    )

    logging.exception(f'Update: {update} \n{exception}')