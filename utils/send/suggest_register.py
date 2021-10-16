from aiogram.types import Message

import keyboards


async def suggest_register(msg: Message):
    await msg.answer("Чтобы люди видели твои лайки, необходимо заполнить небольшую анкету",
                     reply_markup=keyboards.inline.register_btn)