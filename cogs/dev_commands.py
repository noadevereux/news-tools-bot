import disnake
from disnake.ext import commands
from sqlalchemy.exc import IntegrityError

from ext.database.methods import makers as maker_methods, guilds as guild_methods
from ext.models.checks import is_guild_admin
from config import DEV_GUILDS
from ext.models.autocompleters import guild_autocomplete
from ext.tools import get_guild_profile


class DeveloperCommands(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(
        name="dev",
        description="[DEV] Команды разработчика",
        guild_ids=DEV_GUILDS,
        dm_permission=False,
    )
    @is_guild_admin()
    async def dev(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev.sub_command_group(name="guild", description="[DEV] Управление серверами")
    async def dev_guild(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev_guild.sub_command(name="register", description="[DEV] Зарегистрировать сервер")
    async def dev_guild_register(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: disnake.Guild = commands.Param(
            name="guild", description="Discord ID сервера"
        ),
        guild_name: str = commands.Param(
            name="guild_name", description="Название сервера"
        ),
    ):
        await interaction.response.defer()

        if guild_id not in self.bot.guilds:
            return await interaction.edit_original_response(
                content=f"**Бот не является участником сервера `{guild_id.name}`. Сначала пригласите его.**"
            )

        guild = await guild_methods.get_guild(guild_id.id)

        if guild:
            return await interaction.edit_original_response(
                content=f"**Сервер `{guild.guild_name}` уже зарегистрирован.**"
            )

        try:
            await guild_methods.add_guild(discord_id=guild_id.id, guild_name=guild_name)
        except IntegrityError:
            return await interaction.edit_original_response(
                content=f"**Сервер с названием `{guild_name}` уже существует.**"
            )

        return await interaction.edit_original_response(
            content=f"**Вы зарегистрировали сервер `{guild_name}`. Число участников: `{guild_id.member_count}`.**"
        )

    @dev_guild.sub_command(name="activate", description="[DEV] Активировать сервер")
    async def dev_guild_activate(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указанным ID не зарегистрирован.**"
            )

        elif guild.is_active:
            return await interaction.edit_original_response(
                content="**Указанный сервер уже активен.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_active", value=True
        )

        return await interaction.edit_original_response(
            content=f"**Вы активировали сервер `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(name="deactivate", description="[DEV] Деактивировать сервер")
    async def dev_guild_deactivate(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указанным ID не зарегистрирован.**"
            )

        elif not guild.is_active:
            return await interaction.edit_original_response(
                content="**Указанный сервер уже деактивирован.**"
            )

        elif guild.is_admin_guild:
            return await interaction.edit_original_response(
                content="**Указанный сервер является администрирующим. Чтобы деактивировать его сначала снимите права администратора.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_active", value=False
        )

        return await interaction.edit_original_response(
            content=f"**Вы деактивировали сервер `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="info", description="[DEV] Посмотреть информацию о сервере"
    )
    async def dev_guild_info(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным ID не зарегистрирован.**"
            )

        _guild = self.bot.get_guild(guild.discord_id)

        embed = await get_guild_profile(guild_id=guild_id, _guild=_guild)

        return await interaction.edit_original_response(embed=embed)

    @dev_guild.sub_command(name="name", description="[DEV] Изменить имя сервера")
    async def dev_guild_name(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        new_name: str = commands.Param(
            name="new_name", description="Новое имя сервера"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указанным ID не зарегистрирован.**"
            )

        elif guild.guild_name == new_name:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, имя которое вы указали итак установлено серверу.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="guild_name", value=new_name
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили имя сервера с `{guild.guild_name}` на `{new_name}`.**"
        )

    @dev_guild.sub_command(
        name="add_role", description="[DEV] Подключить роль к серверу"
    )
    async def dev_guild_add_role(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        role_id: commands.LargeInt = commands.Param(
            name="role_id", description="Discord ID роли"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        roles_list: list = guild.roles_list

        if role_id in roles_list:
            return await interaction.edit_original_response(
                content="**Роль с указанным Discord ID уже подключена к серверу.**"
            )

        roles_list.append(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            content=f"**Вы подключили роль с ID `{role_id}` к серверу `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="remove_role", description="[DEV] Отключить роль от сервера"
    )
    async def dev_guild_remove_role(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        role_id: commands.LargeInt = commands.Param(
            name="role_id", description="Discord ID роли"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        roles_list: list = guild.roles_list

        if role_id not in roles_list:
            return await interaction.edit_original_response(
                content="**Роль с указанным Discord ID итак не подключена к серверу.**"
            )

        roles_list.remove(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            content=f"**Вы отключили роль с ID `{role_id}` от сервера `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="notifies_enable",
        description="[DEV] Включить уведомления о выдаче и снятии ролей",
    )
    async def dev_guild_notifies_enable(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(name="guild", description="Сервер"),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным ID не зарегистрирован.**"
            )

        elif guild.is_notifies_enabled:
            return await interaction.edit_original_response(
                content=f"**Изменений не произошло, уведомления итак включены для сервера `{guild.guild_name}`.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_notifies_enabled", value=True
        )

        return await interaction.edit_original_response(
            content=f"**Вы включили уведомления о выдаче и снятии ролей для сервера `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="notifies_disable",
        description="[DEV] Отключить уведомления о выдаче и снятии ролей",
    )
    async def dev_guild_notifies_disable(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        elif not guild.is_notifies_enabled:
            return await interaction.edit_original_response(
                content=f"**Изменений не произошло, уведомления итак отключены для сервера `{guild.guild_name}`.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_notifies_enabled", value=False
        )

        return await interaction.edit_original_response(
            content=f"**Вы отключили уведомления о выдаче и снятии ролей для сервера `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="channel", description="[DEV] Изменить рабочий канал для сервера"
    )
    async def dev_guild_channel(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        channel_id: commands.LargeInt = commands.Param(
            default=None, name="channel_id", description="Discord ID канала"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        if not channel_id:
            if not guild.channel_id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, рабочий канал итак не установлен для сервера `{guild.guild_name}`.**"
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="channel_id", value=None
            )

            return await interaction.edit_original_response(
                content=f"**Вы удалили рабочий канал для сервера `{guild.guild_name}`.**"
            )
        elif channel_id:
            if guild.channel_id == channel_id:
                return await interaction.edit_original_response(
                    content="**Изменений не произошло, указанный канал итак установлен в качестве рабочего канала сервера.**"
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="channel_id", value=channel_id
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили рабочий канал для сервера `{guild.guild_name}` на `{channel_id}`.**"
            )

    @dev_guild.sub_command(
        name="add_log_role",
        description="[DEV] Подключить роль для логирования на сервере",
    )
    async def dev_guild_add_log_role(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        role_id: commands.LargeInt = commands.Param(
            name="role_id", description="Discord ID роли"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        roles_list: list = guild.log_roles_list

        if role_id in roles_list:
            return await interaction.edit_original_response(
                content="**Роль с указанным Discord ID уже подключена к логированию на сервере.**"
            )

        roles_list.append(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="log_roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            content=f"**Вы подключили роль с ID `{role_id}` к логированию на сервере `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="remove_log_role",
        description="[DEV] Отключить роль от логирования на сервере",
    )
    async def dev_guild_remove_log_role(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        role_id: commands.LargeInt = commands.Param(
            name="role_id", description="Discord ID роли"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        roles_list: list = guild.log_roles_list

        if role_id not in roles_list:
            return await interaction.edit_original_response(
                content="**Роль с указанным Discord ID итак не подключена к серверу.**"
            )

        roles_list.remove(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="log_roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            content=f"**Вы отключили роль с ID `{role_id}` от логирования на сервере `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="log_roles_channel",
        description="[DEV] Изменить канал для логирования ролей на сервере",
    )
    async def dev_guild_log_roles_channel(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
        channel_id: commands.LargeInt = commands.Param(
            default=None, name="channel_id", description="Discord ID канала"
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        if not channel_id:
            if not guild.log_roles_channel:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, канал итак не установлен для сервера `{guild.guild_name}`.**"
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="log_roles_channel", value=None
            )

            return await interaction.edit_original_response(
                content=f"**Вы удалили канал логирования ролей для сервера `{guild.guild_name}`.**"
            )
        elif channel_id:
            if guild.log_roles_channel == channel_id:
                return await interaction.edit_original_response(
                    content="**Изменений не произошло, указанный канал итак установлен в качестве канала логирования ролей для сервера.**"
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id,
                column_name="log_roles_channel",
                value=channel_id,
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили канал логирования ролей для сервера `{guild.guild_name}` на `{channel_id}`.**"
            )

    @dev_guild.sub_command(
        name="admin_grant", description="[DEV] Выдать серверу административные права"
    )
    async def dev_guild_admin_grant(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        if guild.is_admin_guild:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, сервер итак имеет административные права.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_admin_guild", value=True
        )

        return await interaction.edit_original_response(
            content=f"**Вы предоставили административные права серверу `{guild.guild_name}`.**"
        )

    @dev_guild.sub_command(
        name="admin_revoke",
        description="[DEV] Забрать у сервера административные права",
    )
    async def dev_guild_admin_revoke(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        guild_id: int = commands.Param(
            name="guild", description="Сервер", autocomplete=guild_autocomplete
        ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content="**Сервер с указаным Discord ID не зарегистрирован.**"
            )

        if not guild.is_admin_guild:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, сервер итак не имеет административные права.**"
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_admin_guild", value=False
        )

        return await interaction.edit_original_response(
            content=f"**Вы забрали административные права у сервера `{guild.guild_name}`.**"
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(DeveloperCommands(bot=bot))
