import disnake
from ext.database.methods import guilds as guild_methods, makers as maker_methods


async def guild_autocomplete(
    interaction: disnake.ApplicationCommandInteraction, user_input: str
):
    guilds = await guild_methods.get_all_guilds()

    if len(user_input) == 0:
        return [
            disnake.OptionChoice(name=guild.guild_name, value=str(guild.id))
            for guild in guilds[:25]
        ]
    else:
        sorted_guilds = [
            disnake.OptionChoice(name=guild.guild_name, value=str(guild.id))
            for guild in guilds
            if user_input.lower() in guild.guild_name.lower()
        ]
        return sorted_guilds[:25]


async def maker_autocomplete(
    interaction: disnake.ApplicationCommandInteraction, user_input: str
):
    guild = await guild_methods.get_guild(interaction.guild.id)
    makers = await maker_methods.get_all_makers(guild_id=guild.id)
    if len(user_input) == 0:
        return [
            disnake.OptionChoice(
                name=f"[ID:{maker.id}] {maker.nickname}", value=str(maker.id)
            )
            for maker in makers[:25]
        ]
    else:
        sorted_makers = [
            disnake.OptionChoice(
                name=f"[ID:{maker.id}] {maker.nickname}", value=str(maker.id)
            )
            for maker in makers
            if (user_input.lower() in maker.nickname.lower())
            or (user_input.lower() in str(maker.id))
        ]

        return sorted_makers[:25]
