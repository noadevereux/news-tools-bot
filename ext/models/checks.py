import disnake
from disnake.ext import commands
from ..database.methods import guilds as guild_methods
from .errors import GuildNotExists, CommandCalledInDM


def is_guild_exists():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        if not interaction.guild:
            raise CommandCalledInDM(message="This command is not allowed in DMs")
        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)
        if not guild:
            raise GuildNotExists(message=f"Guild {interaction.guild.id} doesn't exist in the database")
        return True

    return commands.check(predicate)
