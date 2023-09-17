from os import getenv
from dotenv import load_dotenv


load_dotenv("./venv/.env")

PREFIX = "/"
TOKEN = getenv("TOKEN")
MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = getenv("MYSQL_DATABASE")
MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = getenv("MYSQL_PORT")
CHIEF_ROLE_ID = 1040606231489953823
MAKER_ROLE_ID = 885145513949802568
MAKERS_CHAT_ID = 804644436613005372


# https://discord.com/api/oauth2/authorize?client_id=1089657230330183765&permissions=274878237888&scope=applications.commands%20bot
