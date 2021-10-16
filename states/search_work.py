from aiogram.dispatcher.filters.state import State, StatesGroup


class Search(StatesGroup):
    searching_profiles = State()
    write_love_msg = State()

