import logging

from data.config import ADMIN_CHAT_ID
from loader import db, bot
from utils.db_api import redis_commands


async def cur_bot_info(for_chat_id: int):
    clean_likes_count = await db.clean_old_likes(interval=24)

    active_users_count, disable_users_count = await db.get_users_info()
    active_girls_count, disable_girls_count = await db.get_users_info(sex=1)
    active_boys_count, disable_boys_count = await db.get_users_info(sex=2)

    banned_users_count = await db.get_banned_count()
    disable_users_count -= banned_users_count
    all_users_count = active_users_count + disable_users_count + banned_users_count

    users_info_text = f"<b>Статистика по пользователям:</b>\n\n" \
                      f"<i>всего зареганых={all_users_count}; " \
                      f"активные={active_users_count}; " \
                      f"неактивные={disable_users_count}; " \
                      f"забаненные={banned_users_count}</i>\n\n" \
                      f"<i>активные девушки={active_girls_count}; " \
                      f"неактивные девушки={disable_girls_count}\n\n</i>" \
                      f"<i>активные парни={active_boys_count}; " \
                      f"неактивные парни(+ баны)={disable_boys_count}\n\n\n</i>"

    match24_likes_count, all24_likes_count = await db.get_likes_info(interval=24)
    match8_likes_count, all8_likes_count = await db.get_likes_info(interval=8)

    likes_info_text = f"<b>Статистика по лайкам:</b>\n\n" \
                      f"<i>За последние 24 часа: мэтчей={match24_likes_count}; всего лайков={all24_likes_count}</i>\n\n" \
                      f"<i>За последние 8 часов: мэтчей={match8_likes_count}; всего лайков={all8_likes_count}</i>\n\n" \
                      f"<i>Успешно удалено {clean_likes_count} старых лайков</i>"

    info_msg = await bot.send_message(
        chat_id=for_chat_id,
        text=users_info_text+likes_info_text
    )
    await bot.pin_chat_message(
        chat_id=for_chat_id,
        message_id=info_msg.message_id,
        disable_notification=True
    )

    logging.info(f"SCHEDULER CUR BOT INFO FOR REDFRIEND-BOT")