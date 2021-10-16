from aiogram.dispatcher.filters.state import State, StatesGroup


class UserForm(StatesGroup):
    enter_join = State()

    enter_sex = State()
    enter_search = State()
    enter_user_nick = State()
    enter_description = State()
    enter_media = State()

    enter_confirm = State()
