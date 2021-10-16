import logging

from aiogram.types import BotCommand


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand(command="/search", description="🔍 смотреть анкеты"),
            BotCommand(command="/myprofile", description="👤 моя анкета"),
            BotCommand(command="/report", description="⚠️ пожаловаться"),
        ]
    )
    logging.info("Register bot commands")
