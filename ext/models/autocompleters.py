import disnake
from database.methods import makers as maker_methods, guilds as guild_methods, publications as publication_methods


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
    if not guild:
        return

    makers = await maker_methods.get_all_makers(guild_id=guild.id)
    if len(user_input) == 0:
        return [
            disnake.OptionChoice(
                name=f"[ID: {maker.id}] {maker.nickname}", value=str(maker.id)
            )
            for maker in makers[:25]
        ]
    else:
        sorted_makers = [
            disnake.OptionChoice(
                name=f"[ID: {maker.id}] {maker.nickname}", value=str(maker.id)
            )
            for maker in makers
            if (user_input.lower() in maker.nickname.lower())
               or (user_input.lower() in str(maker.id))
        ]

        return sorted_makers[:25]


async def publication_autocomplete(
        interaction: disnake.ApplicationCommandInteraction, user_input: str
):
    guild = await guild_methods.get_guild(interaction.guild.id)
    if not guild:
        return

    publications = await publication_methods.get_all_publications(guild_id=guild.id)
    if len(user_input) == 0:
        return [
            disnake.OptionChoice(
                name=f"[ID: {publication.id}] #{publication.publication_number}",
                value=str(publication.id),
            )
            for publication in publications[:25]
        ]
    else:
        sorted_publications = [
            disnake.OptionChoice(
                name=f"[ID: {publication.id}] #{publication.publication_number}",
                value=str(publication.id),
            )
            for publication in publications
            if (user_input.lower() in str(publication.publication_number).lower())
               or (user_input.lower() in str(publication.id).lower())
        ]

        return sorted_publications[:25]
