import disnake
from ext.database.methods import guilds as guild_methods


async def guild_autocomplete(
        interaction: disnake.ApplicationCommandInteraction,
        user_input: str
):
    guilds = await guild_methods.get_all_guilds()
    if len(user_input) == 0:
        return [disnake.OptionChoice(name=guild.guild_name, value=str(guild.id)) for guild in guilds]
    else:
        return [disnake.OptionChoice(name=guild.guild_name, value=str(guild.id)) for guild in guilds if
                user_input in guild.guild_name]
