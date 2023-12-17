import asyncio
from datetime import datetime

import disnake
from disnake.ext import commands
from sqlalchemy.exc import IntegrityError

from ext.database.methods import guilds as guild_methods
from ext.database.methods import makers as maker_methods
from ext.database.methods import maker_actions as action_methods
from ext.logger import Logger
from ext.tools import *

from ext.models.checks import is_guild_exists
from ext.models.keyboards import get_profile_keyboard
from ext.models.autocompleters import maker_autocomplete, deactivated_maker_autocomplete, active_maker_autocomplete

from config import DEFAULT_POST_TITLES


class Main(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.makers.py.log")

    @commands.slash_command(name="maker", description="Управление редактором", dm_permission=False)
    @is_guild_exists()
    async def maker(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @maker.sub_command(name="register", description="Зарегистрировать редактора в системе")
    async def maker_register(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            nickname: str = commands.Param(name="nickname", description="Никнейм редактора")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=member.id
        )

        if maker and (not maker.account_status):
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе, используйте `/maker activate` чтобы активировать его аккаунт.**"
            )

        elif maker and maker.account_status:
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе и его аккаунт активен.**"
            )

        maker = await maker_methods.add_maker(
            guild_id=guild.id,
            discord_id=member.id,
            nickname=nickname
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="addmaker",
            meta=nickname,
        )

        embed = await get_maker_profile(maker_id=maker.id, user=member)

        return await interaction.edit_original_response(
            content=f"**Вы зарегистрировали редактора {member.mention} `{nickname}` в системе.**",
            embed=embed
        )

    @maker.sub_command(name="activate", description="Активировать аккаунт редактора")
    async def maker_activate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=deactivated_maker_autocomplete),
            nickname: str = commands.Param(name="nickname", description="Никнейм редактора")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе. Используйте `/maker register` чтобы зарегистрировать редактора.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе. Используйте `/maker register` чтобы зарегистрировать редактора.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.account_status:
            return await interaction.edit_original_response(
                content="**Аккаунт редактора итак активен.**"
            )

        timestamp = datetime.now().isoformat()

        tasks = [
            maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="account_status",
                value=True
            ),
            maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="appointment_datetime",
                value=timestamp
            )
        ]

        if not maker.nickname == nickname:
            await maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="nickname",
                value=nickname
            )

        if not maker.level == "1":
            tasks.append(
                maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="level",
                    value="1"
                )
            )

        if not maker.post_name == DEFAULT_POST_TITLES.get(1):
            tasks.append(
                maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="post_name",
                    value=DEFAULT_POST_TITLES.get(1)
                )
            )

        if not maker.status == "active":
            tasks.append(
                maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="status",
                    value="active"
                )
            )

        if not maker.warns == 0:
            tasks.append(
                maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="warns",
                    value=0
                )
            )

        tasks.append(
            action_methods.add_maker_action(
                maker_id=maker.id,
                made_by=interaction_author.id,
                action="addmaker",
                meta=nickname
            )
        )

        await asyncio.gather(*tasks)

        member = interaction.guild.get_member(maker.discord_id)

        if not member:
            return await interaction.edit_original_response(
                content=f"**Вы активировали аккаунт редактора <@{maker.discord_id}> `{nickname}`.**"
            )

        embed = await get_maker_profile(maker_id=maker.id, user=member)

        return await interaction.edit_original_response(
            content=f"**Вы активировали аккаунт редактора <@{maker.discord_id}> `{nickname}`.**",
            embed=embed
        )

    @maker.sub_command(name="deactivate", description="Деактивировать аккаунт редактора")
    async def maker_deactivate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            reason: str = commands.Param(name="reason", description="Причина деактивации")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif not maker.account_status:
            return await interaction.edit_original_response(
                content="**Аккаунт редактора итак деактивирован.**"
            )

        tasks = [
            maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="account_status",
                value=False
            ),
            maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="level",
                value="0"
            )
        ]

        await asyncio.gather(*tasks)

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="deactivate",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы деактивировали аккаунт редактора <@{maker.discord_id}> `{maker.nickname}`. Причина: {reason}.**"
        )

    @commands.slash_command(name="profile", description="Посмотреть профиль редактора", dm_permission=False)
    @is_guild_exists()
    async def maker_profile(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(default=None, name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete)
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )
        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        if not maker_id:
            maker = await maker_methods.get_maker(
                guild_id=guild.id,
                discord_id=interaction.author.id
            )
        else:
            maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Пользователь, которого вы указали, не зарегистрирован в системе.**"
            )

        elif not interaction_author.guild_id == maker.guild_id:
            return await interaction.edit_original_response(
                content="**Пользователь, которого вы указали, не зарегистрирован в системе.**"
            )

        member = interaction.guild.get_member(maker.discord_id)

        embed = await get_maker_profile(maker_id=maker.id, user=member)

        return await interaction.edit_original_response(
            embed=embed,
            view=get_profile_keyboard(maker_id=maker.id)
        )

    @maker.sub_command(name="setdiscord", description="Изменить редактору Discord")
    async def maker_setdiscord(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            new_member: disnake.User | disnake.Member = commands.Param(name="user",
                                                                       description="Пользователь или его ID")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        if await maker_methods.is_maker_exists(guild_id=guild.id, discord_id=new_member.id):
            return await interaction.edit_original_response(
                content="**Пользователь, которого вы указали, уже привязан к какому-то аккаунту.**"
            )

        if maker.discord_id == new_member.id:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, к аккаунту редактора итак привязан указанный дискорд.**"
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="discord_id",
            value=new_member.id
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setdiscord",
            meta=str(new_member.id)
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили Discord редактору с ID `{maker.id}` с <@{maker.discord_id}> на <@{new_member.id}>.**"
        )

    @maker.sub_command(name="setnickname", description="Изменить никнейм редактора")
    async def maker_setnickname(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            nickname: str = commands.Param(name="nickname", description="Никнейм")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.nickname == nickname:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, никнейм, который вы указали, итак принадлежит редактору.**"
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="nickname",
            value=nickname
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setnickname",
            meta=nickname
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили никнейм редактора <@{maker.discord_id}> с `{maker.nickname}` на `{nickname}`.**"
        )

    @maker.sub_command(name="setlevel", description="Изменить уровень доступа редактора")
    async def maker_setlevel(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            level: str = commands.Param(
                name="level",
                description="Уровень доступа",
                choices=[
                    disnake.OptionChoice(name="5", value="5"),
                    disnake.OptionChoice(name="4", value="4"),
                    disnake.OptionChoice(name="3", value="3"),
                    disnake.OptionChoice(name="2", value="2"),
                    disnake.OptionChoice(name="1", value="1"),
                ]
            )
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) <= int(level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**Вы не можете установить редактору уровень доступа, который равнен или выше вашего.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.level == level:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, уровень, который вы указали, итак установлен редактору.**"
            )

        tasks = [maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="level",
            value=level
        ), maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="post_name",
            value=DEFAULT_POST_TITLES.get(int(level))
        )]

        await asyncio.gather(*tasks)

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setlevel",
            meta=level
        )

        return await interaction.edit_original_response(
            content=f"**Вы установили редактору <@{maker.discord_id}> `{maker.nickname}` уровень `{level}`.**"
        )

    @maker.sub_command(name="setpost", description="Установить редактору должность")
    async def maker_setpost(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор или его Discord ID",
                                           autocomplete=active_maker_autocomplete),
            post: str = commands.Param(default=None, name="post", description="Должность редактора")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        if post:

            if maker.post_name == post:
                return await interaction.edit_original_response(
                    content="**Изменений не произошло, должность, которую вы указали, итак принадлежит редактору.**"
                )

            await maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="post_name",
                value=post
            )

            await action_methods.add_maker_action(
                maker_id=maker.id,
                made_by=interaction_author.id,
                action="setpost",
                meta=post
            )

            return await interaction.edit_original_response(
                content=f"**Вы установили редактору <@{maker.discord_id}> `{maker.nickname}` должность `{post}`.**"
            )

        elif not post:

            if maker.post_name == DEFAULT_POST_TITLES.get(int(maker.level)):
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, у редактора итак установлена стандартная должность.**"
                )

            await maker_methods.update_maker(
                guild_id=guild.id,
                discord_id=maker.discord_id,
                column_name="post_name",
                value=DEFAULT_POST_TITLES.get(int(maker.level))
            )

            await action_methods.add_maker_action(
                maker_id=maker.id,
                made_by=interaction_author.id,
                action="setpost",
                meta=DEFAULT_POST_TITLES.get(int(maker.level))
            )

            return await interaction.edit_original_response(
                content=f"**Вы установили редактору <@{maker.discord_id}> `{maker.nickname}` стандартную должность `{DEFAULT_POST_TITLES.get(int(maker.level))}`.**"
            )

    @maker.sub_command(name="setstatus", description="Изменить статус редактора")
    async def maker_setstatus(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            status: str = commands.Param(
                name="status",
                description="Статус",
                choices=[
                    disnake.OptionChoice(name="Активен", value="active"),
                    disnake.OptionChoice(name="Неактивен", value="inactive"),
                ]
            )
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.status == status:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, статус, который вы указали, уже установлен редактору.**"
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="status",
            value=status
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setstatus",
            meta=status
        )

        status_title = await get_status_title(status)

        return await interaction.edit_original_response(
            content=f"**Вы установили редактору <@{maker.discord_id}> `{maker.nickname}` статус `{status_title}`.**"
        )

    @maker.sub_command_group(name="warn", description="Управление наказаниями редактора")
    async def maker_warn(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        pass

    @maker_warn.sub_command(name="give", description="Выдать редактору выговор")
    async def maker_warn_give(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            reason: str = commands.Param(name="reason", description="Причина")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="warns",
            value=(maker.warns + 1)
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="warn",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы выдали выговор редактору <@{maker.discord_id}> `{maker.nickname}`. Причина: {reason}**"
        )

    @maker_warn.sub_command(name="take", description="Снять редактору выговор")
    async def maker_warn_take(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(name="maker", description="Редактор",
                                           autocomplete=active_maker_autocomplete),
            reason: str = commands.Param(name="reason", description="Причина")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and not interaction_author.is_admin:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        if maker.warns <= 0:
            return await interaction.edit_original_response(
                content="**Вы не можете установить отрицательное кол-во выговоров редактору.**"
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="warns",
            value=(maker.warns - 1)
        )

        await action_methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="unwarn",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы сняли выговор редактору <@{maker.discord_id}> `{maker.nickname}`. Причина: {reason}**"
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(Main(bot=bot))
