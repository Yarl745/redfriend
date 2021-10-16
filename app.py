import logging

from aiogram import executor

from data.config import ADMIN_CHAT_ID
from loader import dp, scheduler, db
import middlewares, filters, handlers
from utils import jobs
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def schedule_jobs():
    scheduler.add_job(jobs.cur_bot_info, 'cron', day_of_week='mon-sun', hour=0, minute=0, args=(ADMIN_CHAT_ID,))
    scheduler.add_job(jobs.cur_bot_info, 'cron', day_of_week='mon-sun', hour=8, minute=0, args=(ADMIN_CHAT_ID,))
    scheduler.add_job(jobs.cur_bot_info, 'cron', day_of_week='mon-sun', hour=16, minute=0, args=(ADMIN_CHAT_ID,))


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    await schedule_jobs()

    await db.create_all_tables_ine()

    logging.info("~~~~~~~~~~~~~~~~~~~~~~~START BOT~~~~~~~~~~~~~~~~~~~~~~~")


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup,
                           allowed_updates=[
                               "message", "edited_message", "channel_post", "edited_channel_post",
                               "callback_query", "pre_checkout_query", "poll", "poll_answer",
                               "my_chat_member", "chat_member"
                           ])

