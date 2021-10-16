import re


def get_parse_data(profile_text: str) -> dict:
    l = profile_text.split(", ", maxsplit=2)
    description = ""

    if l[-1].count("–") > 0:
        description = re.sub(r".+– ", "", l[-1], count=1)

    return dict(user_nick=l[0], description=description)