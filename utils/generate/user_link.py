from loader import bot


async def user_link(user_id: int, user_nick=None):
    return (await bot.get_chat_member(user_id, user_id)).user.get_mention(name=user_nick) if user_id > 100000 \
        else user_nick
