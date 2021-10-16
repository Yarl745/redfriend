from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
HOST = env.str("HOST")  # host.docker.internal

PG_USER = env.str("PG_USER")
PG_DB = env.str("PG_DB")
PG_PASSWORD = env.str("PG_PASSWORD")
PG_PORT = env.str("PG_PORT")

DEFAULT_PHOTO = "AgACAgIAAxkBAAIBmGFJNEZlqWFzB-RPyKfPaGXEJqu_AAL1tTEbO7lIShXV09ZRu1r0AQADAgADbQADIAQ"

REPORTS_CHAT_ID = env.str("REPORTS_CHAT_ID")
ERRORS_CHAT_ID = env.str("ERRORS_CHAT_ID")
ADMIN_CHAT_ID = env.str("ADMIN_CHAT_ID")

REDIS_PASS = env.str("REDIS_PASS")  # @cZ%#O&kbyMCN0Y6LWuwbP!b%La0xJY$vIjWEnDwYXl!u3RT&N
REDIS_PORT = env.str("REDIS_PORT")

DEFAULT_PHOTO_ID = env.str("DEFAULT_PHOTO_ID")
ANIMATION_MENU_ID = env.str("ANIMATION_MENU_ID")
ANIMATION_KEYBOARD_ID = env.str("ANIMATION_KEYBOARD_ID")