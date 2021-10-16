import logging
import time
from typing import List

from aiogram.types import User

from loader import cache, likes, searches


async def is_active(user_id: int) -> bool:
    user = User.get_current()
    is_user_exist = await cache.hexists(user_id, "likes_send")
    logging.info(f"User @{user.username}-{user.id} active({is_user_exist})")
    return is_user_exist


async def ban_user(user_id: int):
    await cache.set(f"b{user_id}", time.time())
    logging.info(f"BAN USER-{user_id} in redis")


async def unban_user(user_id: int):
    await cache.delete(f"b{user_id}")
    logging.info(f"UNBAN USER-{user_id} in redis")


async def is_ban(user_id: int) -> bool:
    out = await cache.exists(f"b{user_id}")
    return out


async def get_banned_count() -> int:
    cursor = b'0'
    ban_count = 0
    while cursor:
        cursor, keys = await cache.scan(cursor)
        for key in keys:
            if key[0] == 98:
                ban_count += 1

    return ban_count


async def set_last_profile_id(user_id: int, last_profile_id: int):
    user = User.get_current()

    await cache.hset(user_id, "last_profile_id", last_profile_id)
    logging.info(f"For User @{user.username}-{user.id} SET last profile id({last_profile_id})")


async def del_last_profile_id(user_id: int) -> int:
    user = User.get_current()

    last_profile_id = await cache.hget(user_id, "last_profile_id")
    last_profile_id = int(last_profile_id) if last_profile_id else 0

    if last_profile_id:
        await cache.hdel(user_id, "last_profile_id")

    logging.info(f"For User @{user.username}-{user.id} DEL last profile id({last_profile_id})")
    return last_profile_id


async def activate_user(user_id: int) -> bool:
    user = User.get_current()

    # if is_active(user_id):
    #     logging.info(f"User @{user.username}-{user.id} is already activated in redis_db")
    #     return False

    values = dict(
        likes_send=0,
        likes_get=0
    )

    async with cache.client() as conn:
        await conn.hmset(
            user_id,
            values
        )

    logging.info(f"Activate User @{user.username}-{user.id} in redis_db")
    return True


async def get_search_id(for_user_id: int) -> int:
    search_id = await searches.lpop(for_user_id)

    # byte b'p' == 112
    if search_id and search_id[0] == 112:
        await searches.rpush(for_user_id, search_id)
        search_id = 0
    elif search_id:
        await searches.rpush(for_user_id, f"p{search_id.decode()}")
    else:
        search_id = 0

    return int(search_id) if search_id else 0


async def get_last_search_ids(for_user_id: int) -> List[str]:
    user = User.get_current()

    last_search_ids = await searches.lrange(for_user_id, 0, -1)
    last_search_ids = [search_id[1:].decode() for search_id in last_search_ids] if last_search_ids else []

    logging.info(f"For User @{user.username}-{user.id} get last search ids(count={len(last_search_ids)})")
    return last_search_ids


async def update_search_ids(for_user_id: int, search_ids: list):
    user = User.get_current()
    if search_ids:
        await searches.delete(for_user_id)
        await searches.lpush(for_user_id, *search_ids)
        logging.info(f"For @{user.username}-{user.id} update searches")
    else:
        logging.info(f"For @{user.username}-{user.id} NOT ENOUGH users to update searches")


async def clear_search_ids(for_user_id: int):
    user = User.get_current()
    await searches.delete(for_user_id)
    logging.info(f"Clear search ids for User @{user.username}-{user.id}")


async def clear_all_search_ids():
    await searches.flushdb(asynchronous=True)
    logging.info("Clear ALL search ids in redis db")


async def clear_user(user_id: int):
    user = User.get_current()
    await cache.delete(user_id)
    logging.info(f"Clear cache for User @{user.username}-{user.id}")


async def get_user_cache(user_id: int) -> dict:
    user = User.get_current()
    user_cache = await cache.hgetall(user_id)
    logging.info(f"For User @{user.username}-{user.id} get redis cache {user_cache}")
    return user_cache


async def incr_likes(user_id: int):
    user = User.get_current()

    async with cache.pipeline(transaction=True) as pipe:
        res = await pipe.hincrby(user_id, "likes")

    logging.info(f"User @{user.username}-{user.id} incr likes({res})")


async def add_like(from_user_id: int, to_user_id: int, with_msg=False) -> int:
    likes_count = await likes.lpush(to_user_id, f"l{from_user_id}{'m' if with_msg else ''}")
    await cache.hincrby(from_user_id, "likes_send")
    await cache.hincrby(to_user_id, "likes_get")
    return likes_count


async def add_love_msg(from_user_id: int, to_user_id: int, msg_text: str):
    await likes.set(f"m{from_user_id}{to_user_id}", msg_text)
    logging.info(f"Add love msg to redis {from_user_id}-{to_user_id} (from user to user)")


async def get_love_msg(from_user_id, to_user_id) -> str:
    key = f"m{from_user_id}{to_user_id}"
    love_msg = await likes.get(key)
    await likes.delete(key)
    logging.info(f"Get love msg from redis {from_user_id}-{to_user_id} (from user to user)")
    return love_msg.decode("utf-8") if love_msg else ""


async def add_match(from_user_id: int, to_user_id: int) -> int:
    likes_count = await likes.rpush(to_user_id, from_user_id)
    await cache.hincrby(from_user_id, "likes_send")
    await cache.hincrby(to_user_id, "likes_get")
    return likes_count


async def get_matches(for_user_id: int) -> List[int]:
    user = User.get_current()
    # b'l' == 108
    match_user_ids = [int(user_id) for user_id in await likes.lrange(for_user_id, 0, -1) if user_id[0] != 108]
    await likes.delete(for_user_id)

    logging.info(f"Get likes({len(match_user_ids)}) for User @{user.username}-{user.id}")

    return match_user_ids


async def get_like(for_user_id: int) -> (int, str):
    user = User.get_current()
    from_user_id = 0
    from_user_love_msg = None
    like_user_id = await likes.lpop(for_user_id)

    # b'l' == 108  b'm' == 109
    if like_user_id and like_user_id[0] == 108:
        if like_user_id[-1] == 109:
            from_user_id = int(like_user_id[1:-1])
            from_user_love_msg = await get_love_msg(from_user_id, for_user_id)
        else:
            from_user_id = int(like_user_id[1:])
    elif like_user_id:
        await likes.lpush(for_user_id, like_user_id)

    logging.info(f"For User @{user.username}-{user.id} get like({from_user_id if from_user_id else 'NotFound'}) "
                 f"{'with love msg' if from_user_love_msg else ''}")

    return from_user_id, from_user_love_msg


async def update_last_click(user_id: int):
    await cache.hset(user_id, "last_click", time.time())
