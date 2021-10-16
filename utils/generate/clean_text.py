import re

from aiogram.types import Message


def clean_text(msg: Message) -> str:
    text = msg.text
    entities = msg.entities

    while entities:
        entity = entities.pop(0)
        length = entity["length"]
        offset = entity["offset"]
        text = text.replace(text[offset:offset+length], "`"*length)

    return re.sub(r"`+", "***", text)