from os import getenv

### Temp variable
# This variable serves as a temporarly storage for a service data. It should not be assigned manually

temp = {"startup_time": None}

####################

TOKEN = getenv("TOKEN")

# List of guild ids on which dev commands should be registered
DEV_GUILDS = (1171526838795898920,)

MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = getenv("MYSQL_DATABASE")
MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = getenv("MYSQL_PORT")

JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")

DEFAULT_POST_TITLES = {
    0: None,
    1: "Редактор",
    2: "Заместитель главного редактора",
    3: "Главный редактор",
    4: "Куратор",
    5: "Руководитель",
}

# Ids of emoji which is used in service messages
# Preferably they should be created in the application itself on developer portal
REUSABLE_EMOJI = {
    "pending": "<a:blurple_loading:1233390095336472689>",
    "success": "<a:success:1261226409901293608>",
    "fail": "<a:fail:1261225205678735440>"
}
