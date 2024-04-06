import disnake
from disnake.ext import commands

from database.methods import publication_actions as action_methods, makers as maker_methods, guilds as guild_methods, \
    publications as publication_methods
from ext.logger import Logger
from ext.models.autocompleters import publication_autocomplete
from ext.models.checks import is_guild_exists
from components.publication_components import GearButton, PublicationListPaginator
from ext.profile_getters import get_publication_profile


class Publications(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.publications.py.log")

    @commands.slash_command(
        name="publication", description="Действия с выпусками", dm_permission=False
    )
    @is_guild_exists()
    async def publication(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @publication.sub_command(name="create", description="Создать выпуск")
    async def publication_create(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            publication_number: int = commands.Param(name="number", description="Номер выпуска"),
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

        publication = await publication_methods.get_publication(
            guild_id=guild.id, publication_number=publication_number
        )

        if publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{publication_number}` уже существует.**"
            )

        new_publication = await publication_methods.add_publication(
            guild_id=guild.id, publication_number=publication_number
        )

        await action_methods.add_pub_action(
            pub_id=new_publication.id, made_by=interaction_author.id, action="createpub"
        )

        embed = await get_publication_profile(publication_id=new_publication.id)
        view = GearButton(author=interaction.author, publication_id=new_publication.id)

        return await interaction.edit_original_response(
            content=f"**Вы создали выпуск `#{new_publication.publication_number}`.**",
            embed=embed,
            view=view
        )

    @publication.sub_command(name="info", description="Посмотреть информацию о выпуске")
    async def publication_info(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            publication_id: int = commands.Param(
                name="number",
                description="Номер выпуска",
                autocomplete=publication_autocomplete,
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

        publication = await publication_methods.get_publication_by_id(id=publication_id)

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуска с указанным `ID: {publication_id}` не существует.**"
            )

        elif not publication.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                content=f"**Выпуска с указанным `ID: {publication_id}` не существует.**"
            )

        embed = await get_publication_profile(publication_id=publication.id)

        if int(interaction_author.level) < 2:
            return await interaction.edit_original_response(embed=embed)
        else:
            view = GearButton(author=interaction.author, publication_id=publication.id)
            return await interaction.edit_original_response(embed=embed, view=view)

    @publication.sub_command(name="list", description="Посмотреть список выпусков")
    async def publication_list(self, interaction: disnake.ApplicationCommandInteraction):
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

        view, embed = await PublicationListPaginator.create(guild_id=guild.id)

        return await interaction.edit_original_response(embed=embed, view=view)


def setup(bot: commands.InteractionBot):
    bot.add_cog(cog=Publications(bot=bot))
