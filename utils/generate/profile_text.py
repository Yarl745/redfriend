def profile_text(user_data: dict) -> str:
    user_nick = user_data['user_nick']

    description = f"— {user_data['description']}" if user_data['description'] else ""

    return f"{user_nick} {description}\n\n"
