import re
import disnake
from disnake.colour import Colour
from disnake import Embed, User

from .database.methods import makers as maker_methods, publications as publication_methods


async def get_level_title(levelnum: int) -> str:
    levelnum = int(levelnum)
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
    maker = await maker_methods.get_maker(discord_id=user.id)

    level = await get_level_title(maker.level)
    status = await get_status_title(maker.status)
    publications_amount = await maker_methods.get_publications_by_maker(id=maker.id)
    if not publications_amount:
        publications_amount = 0
    else:
        publications_amount = len(publications_amount)

    embed_description = f"""
    **ID аккаунта: `{maker.id}`**
    **Discord: <@{maker.discord_id}>**
    **Никнейм: {maker.nickname}**
    **Должность: {level}**
    **Статус: {status}**

    **Сделано выпусков: {publications_amount}**
    **Предупреждения: {maker.warns}**
    """

    embed = Embed(
        title=f"Профиль редактора {user.display_name}",
        color=0x2B2D31,
        description=embed_description,
        timestamp=maker.appointment_datetime,
    )

    if not maker.account_status:
        embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

    embed.set_thumbnail(user.display_avatar.url)
    embed.set_footer(text="Дата постановления:")

    return embed


async def get_publication_profile(publication_id: int) -> Embed:
    publication = await publication_methods.get_publication(publication_id=publication_id)
    maker = await maker_methods.get_maker_by_id(id=publication.maker_id)
    if not maker:
        maker = "`не указан`"
    else:
        maker = f"<@{maker.discord_id}> `{maker.nickname}`"

    information_creator = await maker_methods.get_maker_by_id(id=publication.information_creator_id)
    if not information_creator:
        information_creator = "`не указан`"
    else:
        information_creator = (
            f"<@{information_creator.discord_id}> `{information_creator.nickname}`"
        )

    dp_paid_by = await maker_methods.get_maker_by_id(id=publication.salary_payer_id)
    if not dp_paid_by:
        dp_paid_by = "`не выплачено`"
    else:
        dp_paid_by = f"<@{dp_paid_by.discord_id}> `{dp_paid_by.nickname}`"

    if not publication.date:
        date = "`не указана`"
    else:
        date = publication.date.strftime("%d.%m.%Y")

    if not publication.amount_dp:
        amount_dp = "`не установлено`"
    else:
        amount_dp = f"{publication.amount_dp} DP"

    status = await get_status_title(status_kw=publication.status)

    embed_description = f"""
    **Номер выпуска: `{publication.publication_number}`**
    **Дата публикации выпуска: {date}**
    **Редактор: {maker}**
    **Статус: {status}**
    **Зарплата за выпуск: {amount_dp}**

    **Информацию для выпуска собрал: {information_creator}**
    **Зарплату выплатил: {dp_paid_by}**
    """

    embed = disnake.Embed(
        title=f"Информация о выпуске `[#{publication.publication_number}]`",
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
