import disnake
from disnake.ext import commands
from database.methods import guilds as guild_methods, makers as maker_methods
from .exceptions import *


def is_guild_exists():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        if not interaction.guild:
            raise CommandCalledInDM(message="This command is not allowed in DMs")
        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)
        if not guild:
            raise GuildNotExists(
                message=f"Guild {interaction.guild.id} doesn't exist in the database"
            )
        elif not guild.is_active:
            raise GuildNotExists(message=f"Guild {interaction.guild.id} is inactive")
        return True

    return commands.check(predicate)


def is_guild_admin():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        if not interaction.guild:
            raise CommandCalledInDM(message="This command is not allowed in DMs")
        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)
        if not guild:
            raise GuildNotExists(
                message=f"Guild {interaction.guild.id} doesn't exist in the database"
            )
        elif not guild.is_active:
            raise GuildNotExists(message=f"Guild {interaction.guild.id} is inactive")
        elif not guild.is_admin_guild:
            raise GuildNotAdmin(
                message=f"Guild {interaction.guild.id} doesn't have an admin privileges"
            )
        return True

    return commands.check(predicate)


def is_user_admin():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        if not interaction.guild:
            raise CommandCalledInDM(message="This command is not allowed in DMs")
        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)
        if not guild:
            raise GuildNotExists(
                message=f"Guild {interaction.guild.id} doesn't exist in the database"
            )

        user = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not user:
            raise UserNotExists()
        elif not user.is_admin:
            raise UserNotAdmin()
        return True

    return commands.check(predicate)
