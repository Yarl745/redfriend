from aiogram.dispatcher.filters.state import State, StatesGroup


class Profile(StatesGroup):
    activate_profile = State()
    profile_action = State()
    disable_profile = State()

