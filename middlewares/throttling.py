import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from utils.db_api import redis_commands


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=0.35, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
            await redis_commands.update_last_click(message.from_user.id)
            # print(handler.__name__)
        except Throttled as t:
            raise CancelHandler()

    async def on_process_callback_query(self, query: types.CallbackQuery, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
            await redis_commands.update_last_click(query.from_user.id)
        except Throttled as t:
            await query.answer("Подожди {} секунд💤".format(limit), show_alert=True)
            raise CancelHandler()

    @staticmethod
    async def message_throttled(message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")

