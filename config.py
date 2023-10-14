from os import getenv
from dotenv import load_dotenv

load_dotenv("./venv/.env")

TOKEN = getenv("TOKEN")

MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = getenv("MYSQL_DATABASE")
MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = getenv("MYSQL_PORT")

CHIEF_ROLE_ID = int(getenv("CHIEF_ROLE_ID"))
MAKER_ROLE_ID = int(getenv("MAKER_ROLE_ID"))
MAKERS_CHAT_ID = int(getenv("MAKERS_CHAT_ID"))

JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")

# https://discord.com/api/oauth2/authorize?client_id=1089657230330183765&permissions=274878237888&scope=applications.commands%20bot
