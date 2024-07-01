import disnake
from disnake.ext import commands

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
from components.maker_components import GearButton, MakersListPaginator
from ext.profile_getters import get_maker_profile


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
            member: disnake.User
                    | disnake.Member = commands.Param(
                name="user", description="Пользователь или его Discord ID"
            ),
            nickname: str = commands.Param(
                name="nickname", description="Никнейм редактора"
            ),
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
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

        maker = await maker_methods.get_maker(guild_id=guild.id, discord_id=member.id)

        if maker and (not maker.account_status):
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе, используйте `/maker activate` чтобы активировать его аккаунт.**"
            )

        elif maker and maker.account_status:
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе и его аккаунт активен.**"
            )

        maker = await maker_methods.add_maker(
            guild_id=guild.id, discord_id=member.id, nickname=nickname
        )

        await logs_methods.add_log(
            maker_id=maker.id,
            log=f"{interaction_author.nickname} зарегистрировал аккаунт редактору {maker.nickname}"
        )

        embed = await get_maker_profile(maker_id=maker.id, user=member)

        return await interaction.edit_original_response(
            content=f"**Вы зарегистрировали редактора {member.mention} `{nickname}` в системе.**",
            embed=embed,
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
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
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
                guild_id=guild.id, discord_id=interaction.author.id
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
        await interaction.response.defer(ephemeral=True)

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
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

        view, embed = await MakersListPaginator.create(guild_id=guild.id)

        return await interaction.edit_original_response(embed=embed, view=view)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Makers(bot=bot))
