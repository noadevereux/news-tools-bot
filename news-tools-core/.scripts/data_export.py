import argparse
from getpass import getpass

parser = argparse.ArgumentParser()
parser.add_argument("--gid", type=int, required=True, help="ID сервера для экспорта данных")
parser.add_argument("--host", type=str, required=True, help="Адрес хоста")
parser.add_argument("--port", type=int, required=False, help="Порт", default=3306)
parser.add_argument("--user", type=str, required=True, help="Имя пользователя")
parser.add_argument("--db", type=str, required=True, help="База данных")
parser.add_argument("filename", type=str, help="Имя файла для сохранения")
args = parser.parse_args()

_guild_id = args.gid
_host = args.host
_port = args.port
_user = args.user
_db = args.db
_filename = args.filename

_password = getpass("Введите пароль: ")

import pandas as pd
from sqlalchemy import create_engine

connection_url = f"mysql+mysqlconnector://{_user}:{_password}@{_host}:{_port}/{_db}"

sync_engine = create_engine(url=connection_url, pool_recycle=21_600)

guild_query = f"SELECT * FROM guilds WHERE id = {_guild_id};"
makers_query = f"SELECT * FROM makers WHERE guild_id = {_guild_id};"
publications_query = f"SELECT * FROM publications WHERE guild_id = {_guild_id};"

df_guild = pd.read_sql(guild_query, sync_engine)
df_makers = pd.read_sql(makers_query, sync_engine)
df_publications = pd.read_sql(publications_query, sync_engine)

maker_ids = ", ".join(f"'{_id}'" for _id in df_makers["id"])
maker_logs_query = f"SELECT * FROM maker_logs WHERE maker_id IN ({maker_ids});"

publication_ids = ", ".join(f"'{_id}'" for _id in df_publications["id"])
publication_actions_query = f"SELECT * FROM publication_actions WHERE publication_id IN ({publication_ids});"

df_maker_logs = pd.read_sql(maker_logs_query, sync_engine)
df_publication_actions = pd.read_sql(publication_actions_query, sync_engine)

def row_to_sql_values(row):
    result = []
    for x in row:
        if pd.isna(x):
            result.append("NULL")
        elif isinstance(x, (int, float)):
            result.append(str(x))
        else:
            val = str(x).replace("'", "''")
            result.append(f"'{val}'")
    return ", ".join(result)


with open(_filename, "w", encoding="utf8") as f:
    f.writelines(
        [
            "SET FOREIGN_KEY_CHECKS=0;\n",
            "SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";\n",
            "START TRANSACTION;\n"
            "SET time_zone = \"+00:00\";\n"
        ]
    )

    f.writelines(["\n", "--\n", "-- Дамп данных таблицы guilds\n", "--\n", "\n"])

    for _, row in df_guild.iterrows():
        values = row_to_sql_values(row)
        sql_insert = f"INSERT INTO guilds VALUES ({values});\n"
        f.write(sql_insert)
    
    f.writelines(["\n", "--\n", "-- Дамп данных таблицы makers\n", "--\n", "\n"])

    for _, row in df_makers.iterrows():
        values = row_to_sql_values(row)
        sql_insert = f"INSERT INTO makers VALUES ({values});\n"
        f.write(sql_insert)

    f.writelines(["\n", "--\n", "-- Дамп данных таблицы maker_logs\n", "--\n", "\n"])

    for _, row in df_maker_logs.iterrows():
        values = row_to_sql_values(row)
        sql_insert = f"INSERT INTO maker_logs VALUES ({values});\n"
        f.write(sql_insert)

    f.writelines(["\n", "--\n", "-- Дамп данных таблицы publications\n", "--\n", "\n"])

    for _, row in df_publications.iterrows():
        values = row_to_sql_values(row)
        sql_insert = f"INSERT INTO publications VALUES ({values});\n"
        f.write(sql_insert)

    f.writelines(["\n", "--\n", "-- Дамп данных таблицы publication_actions\n", "--\n", "\n"])

    for _, row in df_publication_actions.iterrows():
        values = row_to_sql_values(row)
        sql_insert = f"INSERT INTO publication_actions VALUES ({values});\n"
        f.write(sql_insert)

    f.writelines(
        [
            "SET FOREIGN_KEY_CHECKS=1;\n"
            "COMMIT;\n"
        ]
    )

print(f"Экспорт успешно сохранён в {_filename}")
