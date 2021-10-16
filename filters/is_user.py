from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from loader import db


class IsUser(BoundFilter):
    async def check(self, msg: Message, *args) -> bool:
        return await db.is_user(msg.from_user.id)