import disnake
from disnake.ext import commands

from components.maker_components import GearButton, MakersListPaginator
from database.methods import (
    makers as maker_methods,
    maker_logs as logs_methods,
    guilds as guild_methods,
)
from ext.logger import Logger
from ext.models.autocompleters import (
    maker_autocomplete,
)
from ext.models.checks import is_guild_exists
from ext.profile_getters import get_maker_profile
from ext.models.reusable import *


class Makers(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.makers.py.log")

    @commands.slash_command(
        name="maker", description="Управление редактором", dm_permission=False
    )
    @is_guild_exists()
    async def maker(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @maker.sub_command(
        name="register", description="Зарегистрировать редактора в системе"
    )
    async def maker_register(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(
                name="user", description="Пользователь или его Discord ID"
            ),
            nickname: str = commands.Param(
                name="nickname", description="Никнейм редактора"
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        maker = await maker_methods.get_maker(guild_id=guild.id, discord_id=member.id)

        if maker and (not maker.account_status):
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор уже зарегистрирован в системе с никнеймом **{maker.nickname}**.")
            )

        elif maker and maker.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор уже зарегистрирован в системе с никнеймом **{maker.nickname}** и его аккаунт активен.")
            )

        maker = await maker_methods.add_maker(
            guild_id=guild.id, discord_id=member.id, nickname=nickname
        )

        await logs_methods.add_log(
            maker_id=maker.id,
            log=f"{interaction_author.nickname} зарегистрировал аккаунт редактору {maker.nickname}"
        )

        if guild.duty_role_id:
            member = interaction.guild.get_member(maker.discord_id)
            duty_role = interaction.guild.get_role(guild.duty_role_id)

            try:
                await member.add_roles(duty_role, reason=f"{interaction_author.nickname} зарегистрировал аккаунт")
            except (disnake.HTTPException, disnake.Forbidden) as error:
                channel = interaction.guild.get_channel(guild.channel_id)

                try:
                    if isinstance(error, disnake.HTTPException):
                        await channel.send(
                            content=f"Мне не удалось выдать роль {duty_role.mention} участнику {member.mention}.\n"
                                    f"Произошла внутренняя ошибка при выполнении запроса."
                        )
                    elif isinstance(error, disnake.Forbidden):
                        await channel.send(
                            content=f"Мне не удалось выдать роль {duty_role.mention} участнику {member.mention}.\n"
                                    f"У меня недостаточно прав для выполнения данного действия."
                        )
                except (disnake.HTTPException, disnake.Forbidden):
                    pass

        embed = await get_maker_profile(maker_id=maker.id, user=member)
        view = GearButton(author=interaction.author, maker_id=maker.id)

        return await interaction.edit_original_response(
            embeds=[get_success_embed("Вы зарегистрировали редактора **** в системе."), embed],
            view=view
        )

    @commands.slash_command(
        name="profile", description="Посмотреть профиль редактора", dm_permission=False
    )
    @is_guild_exists()
    async def maker_profile(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            maker_id: int = commands.Param(
                default=None,
                name="maker",
                description="Редактор",
                autocomplete=maker_autocomplete,
            ),
    ):
        await interaction.response.send_message(embed=get_pending_embed())

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )
        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        if not maker_id:
            maker = await maker_methods.get_maker(
                guild_id=guild.id, discord_id=interaction.author.id
            )
        else:
            maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Пользователь с ID **{maker_id}** не зарегистрирован в системе.")
            )

        elif not interaction_author.guild_id == maker.guild_id:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Пользователь с ID **{maker_id}** не зарегистрирован в системе.")
            )

        member = interaction.guild.get_member(maker.discord_id)

        embed = await get_maker_profile(maker_id=maker.id, user=member)

        if (
                not (
                        (int(interaction_author.level) <= int(maker.level))
                        or (interaction_author.id == maker.id)
                )
        ) or interaction_author.is_admin:
            view = GearButton(
                author=interaction.author,
                maker_id=maker.id,
            )

            return await interaction.edit_original_response(embed=embed, view=view)
        else:
            return await interaction.edit_original_response(embed=embed)

    @commands.slash_command(
        name="makerslist",
        description="Список редакторов, зарегистрированных в системе",
        dm_permission=False,
    )
    @is_guild_exists()
    async def makers_list(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message(embed=get_pending_embed(), ephemeral=True)

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данной команды.")
            )

        view, embed = await MakersListPaginator.create(guild_id=guild.id)

        return await interaction.edit_original_response(embed=embed, view=view)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Makers(bot=bot))
