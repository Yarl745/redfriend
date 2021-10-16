from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from loader import db
from utils.db_api import redis_commands


class IsActive(BoundFilter):
    async def check(self, msg: Message, *args) -> bool:
        return await redis_commands.is_active(msg.from_user.id)