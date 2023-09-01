import re
import disnake
from disnake.colour import Colour
from disnake import Embed, User
from utils.databases.main_db import MainDataBase, PublicationsTable
import datetime

main_db = MainDataBase()
pub_db = PublicationsTable()


async def get_level_title(levelnum: int) -> str:
    if levelnum == 1:
        level = "Редактор"
    elif levelnum == 2:
        level = "Заместитель главного редактора"
    elif levelnum == 3:
        level = "Главный редактор"
    elif levelnum == 4:
        level = "Куратор"
    elif levelnum == -1:
        level = "Хранитель"
    else:
        level = "`Ошибка`"
    return level


async def get_status_title(status_kw: str) -> str:
    if status_kw == "new":
        status = "На испытательном сроке"
    elif status_kw == "active":
        status = "Активен"
    elif status_kw == "inactive":
        status = "Неактивен"
    elif status_kw == "in_process":
        status = "В процессе"
    elif status_kw == "completed":
        status = "Сделан"
    elif status_kw == "failed":
        status = "Провален"
    else:
        status = "`Ошибка`"
    return status


async def get_color_object(color_hex: str) -> Colour:
    color = Colour(int(color_hex, base=16))
    return color


async def get_maker_profile(user: User) -> Embed:
    maker = await main_db.get_maker(discord_id=user.id)

    level = await get_level_title(maker[3])
    status = await get_status_title(maker[4])
    publications_amount = await pub_db.get_publications_by_maker(id=maker[0])
    if not publications_amount:
        publications_amount = 0
    else:
        publications_amount = len(publications_amount)

    appointment_datetime = datetime.datetime.fromisoformat(maker[6])

    embed_description = f"""
    **ID аккаунта: `{maker[0]}`**
    **Discord: <@{maker[1]}>**
    **Никнейм: {maker[2]}**
    **Должность: {level}**
    **Статус: {status}**

    **Сделано выпусков: {publications_amount}**
    **Предупреждения: {maker[5]}**
    """

    embed = Embed(
        title=f"Профиль редактора {user.display_name}",
        color=0x2B2D31,
        description=embed_description,
        timestamp=appointment_datetime,
    )

    if maker[7] == 0:
        embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

    embed.set_thumbnail(user.display_avatar.url)
    embed.set_footer(text="Дата постановления:")

    return embed


async def get_publication_profile(publication_id: int) -> Embed:
    publication = await pub_db.get_publication(id=publication_id)
    maker = await main_db.get_maker_by_id(id=publication[1])
    if not maker:
        maker = "`не указан`"
    else:
        maker = f"<@{maker[1]}> `{maker[2]}`"
    information_creator = await main_db.get_maker_by_id(id=publication[3])
    if not information_creator:
        information_creator = "`не указан`"
    else:
        information_creator = f"<@{information_creator[1]}> `{information_creator[2]}`"
    dp_paid_by = await main_db.get_maker_by_id(id=publication[6])
    if not dp_paid_by:
        dp_paid_by = "`не выплачено`"
    else:
        dp_paid_by = f"<@{dp_paid_by[1]}> `{dp_paid_by[2]}`"

    date = datetime.date.fromisoformat(publication[2]).strftime("%d.%m.%Y")
    status = await get_status_title(status_kw=publication[4])

    embed_description = f"""
    **Номер выпуска: `{publication[0]}`**
    **Дата публикации выпуска: {date}**
    **Редактор: {maker}**
    **Статус: {status}**
    **Зарплата за выпуск: {publication[5]} DP**

    **Информацию для выпуска собрал: {information_creator}**
    **DP выплатил: {dp_paid_by}**
    """

    embed = disnake.Embed(
        title=f"Информация о выпуске #{publication[0]}",
        description=embed_description,
        color=0x2B2D31,
    )
    return embed


async def date_validator(date_string: str):
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    if date_pattern.match(date_string):
        return True
    else:
        return False
