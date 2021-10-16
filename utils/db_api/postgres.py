import logging
from datetime import datetime
from typing import List

import asyncpg
from aiogram.types import User
from asyncpg import Pool
from data import config
from data.config import HOST, PG_PORT, DEFAULT_PHOTO_ID


class Database:
    def __init__(self, pool: Pool) -> None:
        self.pool: Pool = pool

    # CREATE EXTENSION IF NOT EXISTS earthdistance CASCADE;
    #
    # CREATE INDEX IF NOT EXISTS users_location_idx ON Users USING gist (ll_to_earth(lat, lng));

    @classmethod
    async def create(cls):
        logging.info("Connect to Database")

        pool = await asyncpg.create_pool(
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DB,
            host=HOST,
            port=PG_PORT
        )
        return cls(pool)

    async def create_all_tables_ine(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Users(
               id integer PRIMARY KEY,
               username text NOT NULL,
               user_nick text NOT NULL,
               description text,
               sex smallint default 2,
               search smallint default 3,
               media_id text NOT NULL,
               with_video bool default false,
               ban_count smallint default 0,
               is_banned bool default false,
               active bool default true,
               update_time timestamp default now(),
               create_time timestamp default now()
            );
            CREATE INDEX IF NOT EXISTS random_search_idx ON Users(active, sex);
            
            CREATE TABLE IF NOT EXISTS Likes(
               from_user_id integer NOT NULL,
               to_user_id integer NOT NULL,
               match bool default False,
               create_time timestamp default now()
            );
            CREATE UNIQUE INDEX IF NOT EXISTS likes_idx ON Likes(from_user_id, to_user_id);
            
            CREATE TABLE IF NOT EXISTS Reports(
               from_user_id integer NOT NULL,
               to_user_id integer NOT NULL,
               cause text NOT NULL,
               create_time timestamp default now()
            );
            CREATE UNIQUE INDEX IF NOT EXISTS reports_idx ON Reports(from_user_id, to_user_id);
           """
        # CREATE OR REPLACE FUNCTION update_modified_column()
        # RETURNS TRIGGER AS $$
        #     BEGIN
        #         NEW.update_time = now();
        #         RETURN NEW;
        #     END;
        # $$ language 'plpgsql';
        # CREATE TRIGGER IF NOT EXISTS update_user_modtime BEFORE UPDATE ON Users FOR EACH ROW EXECUTE
        #     PROCEDURE update_modified_column();

        await self.pool.execute(sql)
        logging.info("Creat All Tables(if not exist)")

    async def add_user(self, **kwargs):
        columns = ", ".join(kwargs.keys())
        nums = ", ".join([
            f"${num}" for num in range(1, len(kwargs) + 1)
        ])

        sql = """
            INSERT INTO Users({columns}) VALUES ({nums})
                ON CONFLICT DO NOTHING;
        """.format(columns=columns, nums=nums)
        await self.pool.execute(sql, *kwargs.values())

        logging.info(f"Add new USER -> {kwargs}")

    async def update_user(self, user_id, **kwargs) -> bool:
        kwargs.update(update_time=datetime.now())
        updated_fields = ", ".join([
            f"{item}=${num}" for num, item in enumerate(kwargs, start=2)
        ])

        sql = """
            UPDATE Users 
                SET {updated_fields}
                    WHERE id=$1
                        RETURNING True; 
        """.format(updated_fields=updated_fields)

        is_updated = await self.pool.fetchval(sql, user_id, *kwargs.values())

        logging.info(f"Update User-{user_id} to values {kwargs}" if is_updated
                     else f"Try updating not registered User({user_id})")

        return is_updated

    async def activate_user(self, user_id: int, active: bool = True) -> dict:
        sql = """
            UPDATE Users
                SET active = $2
                    WHERE id = $1
                        RETURNING id, username, user_nick, media_id, with_video, description, sex, search;
        """
        user_data = await self.pool.fetch(sql, user_id, active)
        logging.info(f"Activate user({user_id}) in postgres{'(NOT ACTIVATE - BANNED)' if not active else ''}")
        return user_data[0] if len(user_data) > 0 else None

    async def get_user(self, user_id) -> dict:
        sql = """
            SELECT id, username, user_nick, description, media_id, with_video FROM Users
                WHERE id = $1
                    LIMIT 1;
        """

        logging.info(f"Get User-{user_id}")

        return await self.pool.fetchrow(sql, user_id)

    async def get_all_users(self, active=True) -> list:
        sql = """
            SELECT id FROM Users 
                WHERE active=$1 AND id > 100000;
        """
        user_ids = [user["id"] for user in await self.pool.fetch(sql, active)]
        logging.info(f"Get all {'NOT' if not active else ''} ACTIVE USER IDS(count={len(user_ids)})")
        return user_ids

    async def get_cache(self, user_id) -> dict:
        sql = """
            SELECT user_nick, sex, search FROM Users
                WHERE id = $1
                    LIMIT 1;
        """

        logging.info(f"Get Cache for User-{user_id}")

        return await self.pool.fetchrow(sql, user_id)

    async def is_user(self, user_id) -> bool:
        user = User.get_current()
        sql = """
            SELECT True FROM Users 
                WHERE id = $1
                    LIMIT 1;
        """

        out = await self.pool.fetchval(sql, user_id)
        logging.info(f"User @{user.username}-{user.id} is USER({out})")

        return out

    async def get_random_user(self) -> dict:
        searcher = User.get_current()

        sql = """
            SELECT id, username, user_nick, media_id, with_video, description FROM Users
                WHERE active = True
                    ORDER BY random() LIMIT 1;
        """

        user = await self.pool.fetchrow(sql)
        logging.info(f"Get RANDOM User(id={user['id'] if user else 'NotFound'}) "
                     f"for Searcher @{searcher.username}-{searcher.id}")

        return user

    async def get_random_search_ids(self, last_search_ids: List[str], search=3) -> list:
        searcher = User.get_current()
        str_ids = ", ".join(last_search_ids)

        sql = """
               SELECT id FROM Users
                   WHERE {} active = True {}
                       ORDER BY random() LIMIT 15;
           """.format(f"id not in ({str_ids}) AND" if last_search_ids else "",
                      f"AND sex = {search}" if search == 1 or search == 2 else "")

        search_ids = [user['id'] for user in await self.pool.fetch(sql)]
        if searcher.id in search_ids:
            search_ids.remove(searcher.id)

        logging.info(f"Get RANDOM search USER IDS(count={len(search_ids)}) "
                     f"for Searcher @{searcher.username}-{searcher.id}")

        return search_ids

    async def get_count_search(self) -> int:
        searcher = User.get_current()

        sql = """
            SELECT count(*) FROM Users
                WHERE active = True;
        """

        count_search = await self.pool.fetchval(sql)
        logging.info(f"For user @{searcher.username}-{searcher.id} "
                     f"get COUNT SEARCH({count_search})")
        return count_search

    async def add_like(self, from_user_id: int, to_user_id: int) -> bool:
        sql = """
            INSERT INTO Likes(from_user_id, to_user_id) VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                    RETURNING True;
        """
        is_added = await self.pool.fetchval(sql, from_user_id, to_user_id)

        logging.info(f"{'DONT' if not is_added else ''} Add new LIKE -> {from_user_id}-{to_user_id}")

        return is_added

    async def match(self, from_user_id: int, to_user_id: int):
        sql = """
            UPDATE Likes
                SET match=true
                    WHERE from_user_id=$1 AND to_user_id=$2;
        """

        await self.pool.execute(sql, from_user_id, to_user_id)

        logging.info(f"New MATCH {from_user_id}-{to_user_id}")

    async def add_report(self, from_user_id: int, to_user_id: int, cause: str) -> bool:
        sql = """
            INSERT INTO Reports(from_user_id, to_user_id, cause) VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
                    RETURNING True;
        """
        is_added = await self.pool.fetchval(sql, from_user_id, to_user_id, cause)

        logging.info(f"{'DONT' if not is_added else ''} Add new REPORT -> {from_user_id}-{to_user_id}")

        return is_added

    async def ban_user(self, user_id: int) -> bool:
        sql = """
            UPDATE Users
                SET ban_count = ban_count + 1, active = False, is_banned = True
                    WHERE id=$1
                        RETURNING True;
        """

        is_banned = await self.pool.fetchval(sql, user_id)
        logging.info(f"User-{user_id} {'BANNED' if is_banned else 'NOT BANNED(not exists id)'}")

        return is_banned

    async def unban_user(self, user_id: int) -> bool:
        sql = """
            UPDATE Users
                SET active = True, is_banned = False
                    WHERE id=$1
                        RETURNING True;
        """

        is_unbanned = await self.pool.fetchval(sql, user_id)
        logging.info(f"User-{user_id} {'UNBANNED' if is_unbanned else 'NOT UNBANNED(not exists id)'}")

        return is_unbanned

    async def clean_old_likes(self, interval: int = 20) -> int:
        sql = """
            DELETE FROM Likes
                WHERE create_time < now() - INTERVAL '{} HOURS'
                    RETURNING True;
        """.format(interval)

        deleted = await self.pool.fetch(sql)
        logging.info(f"DELETED {len(deleted)} OLD LIKES by Admin")

        return len(deleted)

    async def get_likes_info(self, interval: int = 24) -> tuple:
        sql = """
            SELECT count(*) as count, match from Likes
                where create_time > now() - INTERVAL '{} HOURS'
                    group by match
                        order by count;
        """.format(interval)

        like_items = await self.pool.fetch(sql)

        match_likes_count, all_likes_count = 0, 0
        if len(like_items) > 1:
            match_likes_count = like_items[0]["count"]
            all_likes_count = like_items[1]["count"] + match_likes_count
        elif len(like_items) == 1:
            all_likes_count = like_items[0]["count"]

        return match_likes_count, all_likes_count

    async def get_users_info(self, sex=0):
        sql = """
            SELECT count(*) as count, active from Users
                where username != 'f' {}
                    group by active
                        order by active desc;
        """.format(f'AND sex={sex}' if sex else '')

        user_items = await self.pool.fetch(sql)

        active_users_count, disable_users_count = 0, 0
        if len(user_items) > 1:
            active_users_count = user_items[0]["count"]
            disable_users_count = user_items[1]["count"]
        elif len(user_items) == 1:
            active_users_count = user_items[0]["count"]

        return active_users_count, disable_users_count

    async def get_banned_count(self) -> int:
        sql = """
            SELECT count(*) from Users
                where is_banned = True
        """
        return await self.pool.fetchval(sql)
