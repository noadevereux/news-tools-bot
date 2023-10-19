import disnake
from disnake.ext import commands
from ext.database.methods import guilds as guild_methods
from config import DEV_GUILDS
from sqlalchemy.exc import IntegrityError


class Guilds(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name="guild_register", description="[DEV] Зарегистрировать сервер", guild_ids=DEV_GUILDS)
    @commands.is_owner()
    async def guild_register(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            guild_id: disnake.Guild = commands.Param(name="guild_id", description="Сервер или его Discord ID"),
            guild_name: str = commands.Param(name="guild_name", description="Название сервера")
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


def setup(bot: commands.InteractionBot):
    bot.add_cog(cog=Guilds(bot=bot))
