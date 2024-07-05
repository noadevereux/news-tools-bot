from datetime import datetime

import disnake
from disnake import User, Member, Embed, Guild

from database.methods import (
    makers as maker_methods,
    publications as publication_methods,
    guilds as guild_methods,
    badges as badge_methods,
)
from ext.tools import get_status_title


async def get_maker_profile(maker_id: int, user: User | Member = None) -> Embed:
    maker = await maker_methods.get_maker_by_id(id=maker_id)

    level = int(maker.level)

    if maker.post_name:
        post = maker.post_name
    else:
        post = "не установлено"

    status = get_status_title(maker.status)

    publications_amount = await maker_methods.get_publications_by_maker(id=maker.id)

    if not publications_amount:
        publications_amount = 0
    else:
        publications_amount = len(publications_amount)

    days = (datetime.now() - maker.appointment_datetime).days

    makers_awarded_badges = await badge_methods.get_all_makers_awarded_badges(
        maker_id=maker.id
    )

    badges = []

    for awarded_badge in makers_awarded_badges:
        badge = await badge_methods.get_badge(awarded_badge.badge_id)

        if awarded_badge.awarder_id is None:
            awarder = "News Tools"
        else:
            awarder = await maker_methods.get_maker_by_id(awarded_badge.awarder_id)
            awarder = awarder.nickname

        badges.append(
            {
                "emoji": badge.emoji,
                "name": badge.name,
                "description": badge.description,
                "link": badge.link,
                "timestamp": awarded_badge.award_timestamp,
                "awarder": awarder,
            }
        )

    embed_description = f"""\
{"**Значки: " + " ".join([badge.get("emoji") for badge in badges]) + "**" if len(badges) > 0 else ""}

**<:hashtag:1220792495047184515> ID аккаунта: `{maker.id}`**
**<:discord_icon:1207328653734584371> Discord: <@{maker.discord_id}>**
**<:id_card:1207329341227147274> Никнейм: {maker.nickname}**
**<:access_key:1207330321075535882> Уровень доступа: {level}**
**<:job_title:1207331119176089681>️ Должность: {post}**
**<:status:1207331595497771018> Статус: {status.lower()}**

**<:warn_sign:1207315803893145610> Выговоры: {maker.warns}**
**<:pred_sign:1207316150044590081> Предупреждения: {maker.preds}**

**🗞 Сделано выпусков: {publications_amount}**

**<:yellow_calendar:1207339611911884902> Дней на посту редактора: {days}**
    """

    if maker.is_admin:
        embed_description += (
            "\n\n**🛡️ Пользователь обладает административным доступом**"
        )

    if maker.account_status:
        title_emoji = "<:user:1220792994328875058>"
    else:
        title_emoji = "<:user_red:1223319477308100641>"

    if isinstance(user, (User, Member)):
        embed = Embed(
            title=f"{title_emoji} Профиль редактора {maker.nickname}",
            color=0x2B2D31,
            description=embed_description,
            timestamp=maker.appointment_datetime,
        )

        if not maker.account_status:
            embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

        embed.set_thumbnail(user.display_avatar.url)
    else:
        embed_description += "\n\n**🛠️ Упрощенная версия профиля, так как редактор не является участником сервера."

        embed = Embed(
            title=f"Профиль редактора {maker.nickname}",
            color=0x2B2D31,
            description=embed_description,
            timestamp=maker.appointment_datetime,
        )

        if not maker.account_status:
            embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

    embed.set_footer(text="Дата постановления:")

    badges_description = ""

    for badge in badges:
        badges_description += (
            f"\n\n**{badge.get('emoji')} "
            f"{'[' + badge.get('name') + ']' + '(' + badge.get('link') + ')' if badge.get('link') is not None else badge.get('name')}**"
            f"{' — ' + badge.get('description') if badge.get('description') is not None else ''}."
            f"\nБыл награждён {badge.get('awarder')} {disnake.utils.format_dt(badge.get('timestamp'), style='D')}."
        )

    if len(badges) > 0:
        embed.add_field(name="Значки", value=badges_description, inline=False)

    return embed


async def get_publication_profile(publication_id: int) -> Embed:
    publication = await publication_methods.get_publication_by_id(publication_id)
    maker = await maker_methods.get_maker_by_id(id=publication.maker_id)
    if not maker:
        maker = "`не указан`"
    else:
        maker = f"<@{maker.discord_id}> `{maker.nickname}`"

    information_creator = await maker_methods.get_maker_by_id(
        id=publication.information_creator_id
    )
    if not information_creator:
        information_creator = "`не указан`"
    else:
        information_creator = (
            f"<@{information_creator.discord_id}> `{information_creator.nickname}`"
        )

    salary_payer = await maker_methods.get_maker_by_id(id=publication.salary_payer_id)
    if not salary_payer:
        salary_payer = "`не выплачено`"
    else:
        salary_payer = f"<@{salary_payer.discord_id}> `{salary_payer.nickname}`"

    if not publication.date:
        date = "`не указана`"
    else:
        date = publication.date.strftime("%d.%m.%Y")

    if not publication.amount_dp:
        salary = "`не установлено`"
    else:
        salary = f"{publication.amount_dp}"

    status = get_status_title(status_kw=publication.status)

    embed_description = f"""
    **<:hashtag:1220792495047184515> ID выпуска: `{publication.id}`**
    **<:id_card:1207329341227147274> Номер выпуска: `{publication.publication_number}`**
    **<:yellow_calendar:1207339611911884902> Дата публикации выпуска: {date}**
    **<:user:1220792994328875058> Редактор: {maker}**
    **<:workinprogress:1220793552234086451> Статус: {status.lower()}**
    **<:money:1220793737391771829> Зарплата за выпуск: {salary}**

    **<:user:1220792994328875058> Информацию для выпуска собрал: {information_creator}**
    **<:user:1220792994328875058> Зарплату выплатил: {salary_payer}**
    """

    embed = disnake.Embed(
        title=f"<:job_title:1207331119176089681> Информация о выпуске `[#{publication.publication_number}]`",
        description=embed_description,
        color=0x2B2D31,
    )
    return embed


async def get_guild_profile(guild_id: int, _guild: Guild = None):
    guild = await guild_methods.get_guild_by_id(id=guild_id)

    match guild.is_notifies_enabled:
        case True:
            is_notifies_enabled = "включены"
        case False:
            is_notifies_enabled = "отключены"
        case _:
            is_notifies_enabled = "неизвестно"

    match guild.is_admin_guild:
        case True:
            admin_guild = "да"
        case False:
            admin_guild = "нет"
        case _:
            admin_guild = "неизвестно"

    match guild.is_active:
        case True:
            active = "активен"
        case False:
            active = "деактивирован"
        case _:
            active = "неизвестно"

    roles = ""
    roles_amount = len(guild.roles_list)

    log_roles = ""
    log_roles_amount = len(guild.log_roles_list)

    if isinstance(_guild, Guild):
        iteration = 1

        for role in guild.roles_list:
            role_name = _guild.get_role(role)

            if iteration < roles_amount:
                roles += f"`{role} [{role_name}]`, "
            else:
                roles += f"`{role} [{role_name}]`."

            iteration += 1

        if guild.channel_id:
            channel_id = f"<#{guild.channel_id}> (`{guild.channel_id} | {_guild.get_channel_or_thread(int(guild.channel_id))}`)"
        else:
            channel_id = "`нет`"

        iteration = 1

        for role in guild.log_roles_list:
            role_name = _guild.get_role(role)

            if iteration < log_roles_amount:
                log_roles += f"`{role} [{role_name}]`, "
            else:
                log_roles += f"`{role} [{role_name}]`."

            iteration += 1

        if guild.log_roles_channel:
            log_channel = f"<#{guild.log_roles_channel}> (`{guild.log_roles_channel} | {_guild.get_channel_or_thread(int(guild.log_roles_channel))}`)"
        else:
            log_channel = "`нет`"

        if roles == "":
            roles = "`нет`"

        if log_roles == "":
            log_roles = "`нет`"

        if guild.duty_role_id:
            duty_role = f"`{guild.duty_role_id} [{_guild.get_role(guild.duty_role_id).name}]`"
        else:
            duty_role = "`не установлена`"

        embed_description = f"""\
**ID сервера: `{guild.id}`**
**Discord ID сервера: `{guild.discord_id}`**
**Имя сервера: `{guild.guild_name}`**

**Основная роль: {duty_role}**

**ID подключённых ролей: {roles}**
**Подключённый канал: {channel_id}**

**ID подключённых к логированию ролей: {log_roles}**
**Канал для логирования ролей: {log_channel}**

**Статус уведомлений: `{is_notifies_enabled}`**
**Административный доступ: `{admin_guild}`**
**Статус сервера: `{active}`**
        """
    else:
        iteration = 1

        for role in guild.roles_list:
            if iteration < roles_amount:
                roles += f"`{role}`, "
            else:
                roles += f"`{role}`."

            iteration += 1

        if guild.channel_id:
            channel_id = f"<#{guild.channel_id}> (`{guild.channel_id}`)"
        else:
            channel_id = "`нет`"

        iteration = 1

        for role in guild.log_roles_list:
            if iteration < log_roles_amount:
                log_roles += f"`{role}`, "
            else:
                log_roles += f"`{role}`."

            iteration += 1

        if guild.log_roles_channel:
            log_channel = f"<#{guild.log_roles_channel}> (`{guild.log_roles_channel}`)"
        else:
            log_channel = "`нет`"

        if roles == "":
            roles = "`нет`"

        if log_roles == "":
            log_roles = "`нет`"

        if guild.duty_role_id:
            duty_role = f"`{guild.duty_role_id}`"
        else:
            duty_role = "`не установлена`"

        embed_description = f"""\
**ID сервера: `{guild.id}`**
**Discord ID сервера: `{guild.discord_id}`**
**Имя сервера: `{guild.guild_name}`**

**Основная роль: {duty_role}**

**ID подключённых ролей: {roles}**
**Подключённый канал: {channel_id}**

**ID подключённых к логированию ролей: {log_roles}**
**Канал для логирования ролей: {log_channel}**

**Статус уведомлений: `{is_notifies_enabled}`**
**Административный доступ: `{admin_guild}`**
**Статус сервера: `{active}`**

**🛠️ Внимание, это упрощенная версия информации, т.к. бот не является участником сервера.**
**В упрощенной версии нельзя посмотреть названия ролей и каналов.**
        """

    embed = disnake.Embed(
        title=f"Информация о сервере `{guild.guild_name}`",
        description=embed_description,
        color=0x2B2D31,
    )

    return embed


async def get_badge_profile(badge_id: int) -> Embed:
    badge = await badge_methods.get_badge(badge_id=badge_id)

    if badge.description:
        badge_description = badge.description
    else:
        badge_description = "`не задано`"

    if badge.link:
        badge_link = badge.link
    else:
        badge_link = "`не задана`"

    if badge.is_global:
        badge_is_global = "`да`"
    else:
        badge_is_global = "`нет`"

    guild_names = []

    for guild_id in badge.allowed_guilds:
        guild = await guild_methods.get_guild_by_id(id=guild_id)
        guild_names.append(guild.guild_name)

    if len(guild_names) > 0:
        guild_names = ", ".join(guild_names)
    else:
        guild_names = "`нет`"

    embed_description = f"""\
**ID: {badge.id}**
**Эмодзи: {badge.emoji}**
**Название: `{badge.name}`**
**Описание: {badge_description}**
**Ссылка: {badge_link}**
**Разрешенные сервера: {guild_names}**
**Только глобальный: {badge_is_global}**"""

    embed = disnake.Embed(
        title=f"Информация о значке {badge.emoji} {badge.name}",
        description=embed_description,
        colour=0x2B2D31,
    )

    return embed
