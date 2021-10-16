from aiogram.dispatcher.filters.state import State, StatesGroup


class Trial(StatesGroup):
    how_work = State()

    show_profiles = State()
    search_profiles = State()
    write_love_msg = State()
