from aiogram.dispatcher.filters.state import State, StatesGroup


class Likes(StatesGroup):
    show_likes = State()
    get_like = State()


