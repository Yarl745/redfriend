import asyncio

import aioredis
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aioredis import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data import config
from data.config import REDIS_PASS, HOST, REDIS_PORT
from utils.db_api.postgres import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(password=config.REDIS_PASS, host=HOST, port=REDIS_PORT, db=8)
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
db: Database = loop.run_until_complete(Database.create())

cache: Redis = aioredis.from_url(
    f'redis://{HOST}:{REDIS_PORT}', db=9, password=REDIS_PASS
)
likes: Redis = aioredis.from_url(
    f'redis://{HOST}:{REDIS_PORT}', db=10, password=REDIS_PASS
)
searches: Redis = aioredis.from_url(
    f'redis://{HOST}:{REDIS_PORT}', db=11, password=REDIS_PASS
)

scheduler = AsyncIOScheduler()
