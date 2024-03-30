from datetime import datetime

import disnake
from disnake import User, Member, Embed, Guild

from database.methods import makers as maker_methods, publications as publication_methods, guilds as guild_methods
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

    notes = []

    embed_description = f"""\
**ID аккаунта: `{maker.id}`**
**Discord: <@{maker.discord_id}>**
**Никнейм: {maker.nickname}**
**Уровень доступа: {level}**
**Должность: {post}**
**Статус: {status.lower()}**

**Выговоры: {maker.warns}**
**Предупреждения: {maker.preds}**

**Сделано выпусков: {publications_amount}**

**Дней на посту редактора: {days}**
    """

    if maker.is_admin:
        notes.append("🛡️ Пользователь обладает административным доступом")

    if isinstance(user, (User, Member)):
        for note in notes:
            embed_description += f"\n**{note}.**"

        embed = Embed(
            title=f"Профиль редактора {maker.nickname}",
            color=0x2B2D31,
            description=embed_description,
            timestamp=maker.appointment_datetime,
        )

        if not maker.account_status:
            embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

        embed.set_thumbnail(user.display_avatar.url)
    else:
        notes.append(
            "🛠️ Внимание, это упрощенная версия информации, т.к. бот не смог найти участника"
        )

        for note in notes:
            embed_description += f"\n**{note}.**"

        embed = Embed(
            title=f"Профиль редактора {maker.nickname}",
            color=0x2B2D31,
            description=embed_description,
            timestamp=maker.appointment_datetime,
        )

        if not maker.account_status:
            embed.set_author(name="🔴 АККАУНТ ДЕАКТИВИРОВАН 🔴")

    embed.set_footer(text="Дата постановления:")

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

    status = get_status_title(status_kw=publication.status)

    embed_description = f"""
    **ID выпуска: `{publication.id}`**
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

        embed_description = f"""\
**ID сервера: `{guild.id}`**
**Discord ID сервера: `{guild.discord_id}`**
**Имя сервера: `{guild.guild_name}`**

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

        embed_description = f"""\
**ID сервера: `{guild.id}`**
**Discord ID сервера: `{guild.discord_id}`**
**Имя сервера: `{guild.guild_name}`**

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
