import datetime

import disnake
from disnake.ext import commands
from sqlalchemy.exc import IntegrityError

from database.methods import (
    guilds as guild_methods,
    badges as badge_methods,
    makers as maker_methods,
    publications as publication_methods,
)
from ext.models.checks import is_guild_admin, is_user_admin
from config import DEV_GUILDS, temp
from ext.models.autocompleters import (
    guild_autocomplete,
    badge_autocomplete,
    all_makers_autocomplete,
)
from ext.profile_getters import get_guild_profile, get_badge_profile
from ext.tools import validate_url
from ext.models.reusable import *


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
    @is_user_admin()
    async def dev(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev.sub_command(name="test", description="[DEV] Выполнить тестовую функцию")
    async def dev_test(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message(embed=get_pending_embed(), ephemeral=True)

        makers = await maker_methods.get_all_makers(2)

        makers_guild = [(await maker.awaitable_attrs.guild).guild_name for maker in makers]

        print(makers_guild)

        return await interaction.edit_original_response(embed=get_success_embed("Проверьте вывод в консоли."))

    @dev.sub_command_group(name="service", description="[DEV] Служебные команды")
    async def dev_service(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev_service.sub_command(
        name="stats", description="[DEV] Статистика по использованию приложения"
    )
    async def dev_service_stats(
            self, interaction: disnake.ApplicationCommandInteraction
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        all_makers = await maker_methods.get_all_makers()
        all_publications = await publication_methods.get_all_publications()
        startup_time = temp.get("startup_time")

        stats_message = (
            f"- Кол-во серверов, на которых бот находится: `{len(self.bot.guilds)}`\n"
            f"- Всего зарегистрировано пользователей: `{len(all_makers)}`\n"
            f"- Всего создано выпусков: `{len(all_publications)}`\n\n"
            f"- Приложение было запущено {disnake.utils.format_dt(startup_time, style='R')}"
        )

        embed = disnake.Embed(
            title="Статистика по использованию приложения",
            description=stats_message,
            timestamp=datetime.datetime.now(),
            colour=0x2B2D31,
        )
        embed.set_footer(text="Актуальность информации:")

        return await interaction.edit_original_response(embed=embed)

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
        await interaction.response.send_message(embed=get_pending_embed())

        if guild_id not in self.bot.guilds:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Бот не является участником сервера **{guild_id.name}**.")
            )

        guild = await guild_methods.get_guild(guild_id.id)

        if guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** уже зарегистрирован.")
            )

        try:
            await guild_methods.add_guild(discord_id=guild_id.id, guild_name=guild_name)
        except IntegrityError:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с названием **{guild_name}** уже существует.")
            )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы зарегистрировали сервер **{guild_name}**. Число участников: **{guild_id.member_count}**.")
        )

    @dev_guild.sub_command(name="activate", description="[DEV] Активировать сервер")
    async def dev_guild_activate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            guild_id: int = commands.Param(
                name="guild", description="Сервер", autocomplete=guild_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        elif guild.is_active:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** уже активен.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_active", value=True
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы активировали сервер **{guild.guild_name}**.")
        )

    @dev_guild.sub_command(name="deactivate", description="[DEV] Деактивировать сервер")
    async def dev_guild_deactivate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            guild_id: int = commands.Param(
                name="guild", description="Сервер", autocomplete=guild_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        elif not guild.is_active:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** уже деактивирован.")
            )

        elif guild.is_admin_guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(
                    f"Сервер **{guild.guild_name}** является администрирующим. Чтобы деактивировать его сначала снимите права администратора."
                )
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_active", value=False
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы деактивировали сервер **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        elif guild.guild_name == new_name:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Имя **{new_name}** итак установлено серверу **{guild.guild_name}**.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="guild_name", value=new_name
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы изменили имя сервера с **{guild.guild_name}** на **{new_name}**.")
        )

    @dev_guild.sub_command(
        name="set_duty_role", description="[DEV] Установить основную должностную роль"
    )
    async def dev_guild_set_duty_role(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            guild_id: int = commands.Param(
                name="guild", description="Сервер", autocomplete=guild_autocomplete
            ),
            role_id: commands.LargeInt = commands.Param(
                default=None, name="role_id", description="Discord ID роли"
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        if role_id:
            if role_id == guild.duty_role_id:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Роль с ID **{role_id}** уже указана как основная для сервера **{guild.guild_name}**."
                    )
                )

            await guild_methods.update_guild_by_id(
                id=guild.id,
                column_name="duty_role_id",
                value=role_id
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(
                    f"Вы установили роль с ID **{role_id}** как основную для сервера **{guild.guild_name}**."
                )
            )
        else:
            if not guild.duty_role_id:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(f"Основная роль не указана для сервера **{guild.guild_name}**.")
                )

            await guild_methods.update_guild_by_id(
                id=guild.id,
                column_name="duty_role_id",
                value=None
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(f"Вы удалили основную роль для сервера **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        roles_list: list = guild.roles_list

        if role_id in roles_list:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Роль с ID **{role_id}** уже подключена к серверу **{role_id}**.")
            )

        roles_list.append(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы подключили роль с ID **{role_id}** к серверу **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        roles_list: list = guild.roles_list

        if role_id not in roles_list:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Роль с ID **{role_id}** не подключена к серверу **{guild.guild_name}**.")
            )

        roles_list.remove(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы отключили роль с ID **{role_id}** от сервера **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        elif guild.is_notifies_enabled:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Уведомления уже включены для сервера **{guild.guild_name}**.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_notifies_enabled", value=True
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы включили уведомления о выдаче и снятии ролей для сервера **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        elif not guild.is_notifies_enabled:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Уведомления не включены для сервера **{guild.guild_name}**.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_notifies_enabled", value=False
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы отключили уведомления о выдаче и снятии ролей для сервера **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        if not channel_id:
            if not guild.channel_id:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Рабочий канал не установлен для сервера **{guild.guild_name}**.")
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="channel_id", value=None
            )

            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Вы удалили рабочий канал для сервера **{guild.guild_name}**.")
            )
        elif channel_id:
            if guild.channel_id == channel_id:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Канал с ID **{channel_id}** уже установлен в качестве рабочего канала сервера **{guild.guild_name}**.")
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="channel_id", value=channel_id
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(
                    f"Вы изменили рабочий канал для сервера **{guild.guild_name}** на **{channel_id}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        roles_list: list = guild.log_roles_list

        if role_id in roles_list:
            return await interaction.edit_original_response(
                embed=get_failed_embed(
                    f"Роль с ID **{role_id}** уже подключена к логированию на сервере **{guild.guild_name}**.")
            )

        roles_list.append(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="log_roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы подключили роль с ID **{role_id}** к логированию на сервере **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        roles_list: list = guild.log_roles_list

        if role_id not in roles_list:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Роль с ID **{role_id}** итак не подключена к серверу **{guild.guild_name}**.")
            )

        roles_list.remove(role_id)

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="log_roles_list", value=roles_list
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы отключили роль с ID **{role_id}** от логирования на сервере **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        if not channel_id:
            if not guild.log_roles_channel:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Канал для логирования ролей не установлен для сервера `{guild.guild_name}`.")
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id, column_name="log_roles_channel", value=None
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(f"Вы удалили канал логирования ролей для сервера **{guild.guild_name}**.")
            )
        elif channel_id:
            if guild.log_roles_channel == channel_id:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Канал с ID **{channel_id}** уже установлен в качестве канала логирования ролей для сервера **{guild.guild_name}**.")
                )

            await guild_methods.update_guild(
                discord_id=guild.discord_id,
                column_name="log_roles_channel",
                value=channel_id,
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(
                    f"Вы изменили канал логирования ролей для сервера **{guild.guild_name}** на **{channel_id}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        if guild.is_admin_guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** уже имеет административные права.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_admin_guild", value=True
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы предоставили административные права серверу **{guild.guild_name}**.")
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
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер с ID {guild_id} не зарегистрирован.")
            )

        if not guild.is_admin_guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** не имеет административные права.")
            )

        await guild_methods.update_guild(
            discord_id=guild.discord_id, column_name="is_admin_guild", value=False
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы забрали административные права у сервера **{guild.guild_name}**.")
        )

    @dev.sub_command_group(name="badge", description="[DEV] Управление значками")
    async def dev_badge(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev_badge.sub_command(name="create", description="[DEV] Создать значок")
    async def dev_badge_create(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            name: str = commands.Param(name="name", description="Название значка"),
            emoji: str = commands.Param(name="emoji", description="Эмодзи значка"),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        if_badge_exists = await badge_methods.if_badge_exists(name=name, emoji=emoji)

        if if_badge_exists:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значок **{emoji} {name}** уже существует.")
            )

        badge = await badge_methods.add_badge(name=name, emoji=emoji)

        badge_profile = await get_badge_profile(badge_id=badge.id)

        embeds = [
            get_success_embed(f"Вы создали значок **{emoji} {name}**."),
            badge_profile
        ]

        return await interaction.edit_original_response(
            embeds=embeds
        )

    @dev_badge.sub_command(
        name="info", description="[DEV] Посмотреть информацию о значке"
    )
    async def dev_badge_info(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        embed = await get_badge_profile(badge_id=badge_id)

        return await interaction.edit_original_response(embed=embed)

    @dev_badge.sub_command(name="emoji", description="[DEV] Изменить эмодзи значка")
    async def dev_badge_emoji(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            emoji: str = commands.Param(name="emoji", description="Новый эмодзи"),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )
        elif badge.emoji == emoji:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значку **[{badge.id}] {badge.name}** уже установлен эмодзи **{emoji}**.")
            )

        await badge_methods.update_badge(
            badge_id=badge_id, column_name="emoji", value=emoji
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы изменили эмодзи значку **[{badge.id}] {badge.name}** с **{badge.emoji}** на **{emoji}**.")
        )

    @dev_badge.sub_command(name="name", description="[DEV] Изменить название значка")
    async def dev_badge_name(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            name: str = commands.Param(name="name", description="Новое название"),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )
        elif badge.name == name:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значку **[{badge.id}] {badge.name}** уже установлено это название.")
            )

        await badge_methods.update_badge(
            badge_id=badge_id, column_name="name", value=name
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы изменили название значку **[{badge.id}]** с **{badge.name}** на **{name}**.")
        )

    @dev_badge.sub_command(
        name="description", description="[DEV] Изменить описание значка"
    )
    async def dev_badge_description(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            description: str = commands.Param(
                default=None, name="description", description="Новое описание"
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        if description:
            if badge.description == description:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Значку **[{badge.id}] {badge.name}** уже установлено описание **{description}**.")
                )

            await badge_methods.update_badge(
                badge_id=badge_id, column_name="description", value=description
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(
                    f"Вы изменили описание значку **[{badge.id}] {badge.name}** с **{badge.description if badge.description is not None else 'не задано'}** на **{description}**."
                )
            )
        else:
            if not badge.description:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(f"У значка **[{badge.id}] {badge.name}** отсутствует описание.")
                )

            await badge_methods.update_badge(
                badge_id=badge_id, column_name="description", value=None
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(
                    f"Вы очистили описание **{badge.description}** значка **[{badge.id}] {badge.name}**.")
            )

    @dev_badge.sub_command(name="link", description="[DEV] Изменить ссылку значка")
    async def dev_badge_link(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            link: str = commands.Param(
                default=None, name="link", description="Новая ссылка"
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        if link:
            if not validate_url(link):
                return await interaction.edit_original_response(
                    embed=get_failed_embed(
                        f"Вы указали невалидную ссылку **{link}**. Ссылка должна начинаться на `https://` и вести куда-либо.")
                )

            if badge.link == link:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(f"Значку **[{badge.id}] {badge.name}** уже установлена ссылка **{link}**.")
                )

            await badge_methods.update_badge(
                badge_id=badge_id, column_name="link", value=link
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(f"Вы изменили ссылку значка **[{badge.id}] {badge.name}** с "
                                        f"**{badge.link if badge.link is not None else 'не задана'}** на **{link}**.")
            )
        else:
            if not badge.link:
                return await interaction.edit_original_response(
                    embed=get_failed_embed(f"У значка **[{badge.id}] {badge.name}** отсутствует ссылка.")
                )

            await badge_methods.update_badge(
                badge_id=badge_id, column_name="link", value=None
            )

            return await interaction.edit_original_response(
                embed=get_success_embed(f"Вы очистили ссылку **{badge.link}** у значка **[{badge.id}] {badge.name}**.")
            )

    @dev_badge.sub_command(
        name="add_guild", description="[DEV] Добавить сервер к разрешенным"
    )
    async def dev_badge_add_guild(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            guild_id: int = commands.Param(
                name="guild", description="Сервер", autocomplete=guild_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервера с ID **{guild_id}** не существует.")
            )

        new_allowed_guilds = list(badge.allowed_guilds).copy()

        if guild_id in new_allowed_guilds:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** уже находится в списке разрешенных.")
            )

        new_allowed_guilds.append(guild_id)

        await badge_methods.update_badge(
            badge_id=badge_id, column_name="allowed_guilds", value=new_allowed_guilds
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Сервер **{guild.guild_name}** добавлен в список разрешенных для значка **[{badge.id}] {badge.name}**.")
        )

    @dev_badge.sub_command(
        name="remove_guild", description="[DEV] Удалить сервер из разрешенных"
    )
    async def dev_badge_remove_guild(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            guild_id: int = commands.Param(
                name="guild", description="Сервер", autocomplete=guild_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервера с ID **{guild_id}** не существует.")
            )

        new_allowed_guilds = list(badge.allowed_guilds).copy()

        if guild_id not in new_allowed_guilds:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Сервер **{guild.guild_name}** не находится в списке разрешенных.")
            )

        new_allowed_guilds.remove(guild_id)

        await badge_methods.update_badge(
            badge_id=badge_id, column_name="allowed_guilds", value=new_allowed_guilds
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Сервер **{guild.guild_name}** удалён из списка разрешенных для значка **[{badge.id}] {badge.name}**.")
        )

    @dev_badge.sub_command(
        name="global", description="[DEV] Изменить глобальный статус значка"
    )
    async def dev_badge_global(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            is_global: bool = commands.Param(
                default=False,
                name="is_global",
                description="Глобальный статус значка",
                choices=[
                    disnake.OptionChoice(name="True", value=1),
                    disnake.OptionChoice(name="False (по-умолчанию)", value=0),
                ],
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )
        elif badge.is_global == bool(is_global):
            return await interaction.edit_original_response(
                embed=get_failed_embed(
                    f"У значка **[{badge.id}] {badge.name}** уже установлен глобальный статус **{bool(is_global)}**.")
            )

        await badge_methods.update_badge(
            badge_id=badge_id, column_name="is_global", value=bool(is_global)
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы изменили глобальный статус значка **[{badge.id}] {badge.name}** с **{badge.is_global}** на **{bool(is_global)}**.")
        )

    @dev_badge.sub_command(name="give", description="[DEV] Выдать редактору значок")
    async def dev_badge_give(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(
                name="maker", description="Редактор", autocomplete=all_makers_autocomplete
            ),
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор с ID **{maker_id}** не существует.")
            )

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        awarded_badge = await badge_methods.get_makers_awarded_badge(
            maker_id=maker.id, badge_id=badge.id
        )

        if awarded_badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(
                    f"Редактор **[{maker.id}] {maker.nickname}** уже был награждён значком **[{badge.id}] {badge.name}**.")
            )

        await badge_methods.add_awarded_badge(maker_id=maker.id, badge_id=badge.id)

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы наградили редактора **[{maker.id}] {maker.nickname}** значком **[{badge.id}] {badge.name}**.")
        )

    @dev_badge.sub_command(name="take", description="[DEV] Снять с редактора значок")
    async def dev_badge_take(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(
                name="maker", description="Редактор", autocomplete=all_makers_autocomplete
            ),
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор с ID **{maker_id}** не существует.")
            )

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        awarded_badge = await badge_methods.get_makers_awarded_badge(
            maker_id=maker.id, badge_id=badge.id
        )

        if not awarded_badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(
                    f"Редактор **[{maker.id}] {maker.nickname}** не награждён значком **[{badge.id}] {badge.name}**.")
            )

        await badge_methods.delete_awarded_badge(maker_id=maker.id, badge_id=badge.id)

        return await interaction.edit_original_response(
            embed=get_success_embed(
                f"Вы забрали у редактора **[{maker.id}] {maker.nickname}** значок **[{badge.id}] {badge.name}**.")
        )

    @dev_badge.sub_command(
        name="giveaway", description="[DEV] Начать глобальную раздачу значка"
    )
    async def dev_badge_giveaway(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            badge_id: int = commands.Param(
                name="badge", description="Значок", autocomplete=badge_autocomplete
            ),
            channel: disnake.TextChannel = commands.Param(
                name="channel", description="Канал куда отправить раздачу"
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed(), ephemeral=True)

        badge = await badge_methods.get_badge(badge_id=badge_id)

        if not badge:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Значка с ID **{badge_id}** не существует.")
            )

        button = disnake.ui.Button(
            style=disnake.ButtonStyle.green,
            label="Получить значок",
            custom_id=f"badge_giveaway:{badge.id}",
            emoji=badge.emoji,
        )

        await channel.send(
            content=f"## Запущена раздача значка «{badge.name}»\n"
                    f"> Нажмите на кнопку чтобы получить значок на все свои аккаунты.\n\n"
                    f"Информация о значке:\n"
                    f"Эмодзи: {badge.emoji}\n"
                    f"Название: {badge.name}\n"
                    f"Описание: {badge.description if badge.description is not None else 'не задано'}\n"
                    f"Ссылка значка: {badge.link if badge.link is not None else 'не задана'}",
            components=button,
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы запустили раздачу значка **[{badge.id}] {badge.name}**.")
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(DeveloperCommands(bot=bot))
