import logging

from data.config import ADMIN_CHAT_ID, UNIVERSITY_NAME
from loader import db, bot


async def cleaning():
    count = await db.clean_old_likes(interval=24)

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text="В {} городке успешно удалено {} старых лайков(за {} hours)".format(UNIVERSITY_NAME, count, 24)
    )

    logging.info(f"SCHEDULER CLEAN OLD LIKES(count={count})")