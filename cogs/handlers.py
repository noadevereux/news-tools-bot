import disnake
from disnake.ext import commands

from database.methods import badges as badge_methods, makers as maker_methods, guilds as guild_methods


async def on_badge_giveaway_button_click(interaction: disnake.MessageInteraction):
    if not str(interaction.component.custom_id).startswith("badge_giveaway"):
        return

    await interaction.response.defer(ephemeral=True, with_message=True)

    badge_id = int(str(interaction.component.custom_id).split(":")[1])

    badge = await badge_methods.get_badge(badge_id=badge_id)

    if not badge:
        return interaction.edit_original_response(
            content="**Видимо раздача уже неактуальна. Значка, который раздается уже не существует.**"
        )

    makers_accounts = await maker_methods.get_all_makers_by_discord_id(discord_id=interaction.author.id)

    given_accounts = []
    rejected_accounts = []

    for maker in makers_accounts:
        awarded_badges = await badge_methods.get_all_makers_awarded_badges(maker_id=maker.id)
        guild = await guild_methods.get_guild_by_id(maker.guild_id)

        should_continue = False

        for awarded_badge in awarded_badges:
            if awarded_badge.badge_id == badge.id:
                rejected_accounts.append({
                    "nickname": maker.nickname,
                    "guild_name": guild.guild_name
                })

                should_continue = True
                break

        if should_continue:
            continue

        await badge_methods.add_awarded_badge(maker_id=maker.id, badge_id=badge.id)

        given_accounts.append({
            "nickname": maker.nickname,
            "guild_name": guild.guild_name
        })

    if len(given_accounts) > 0 and len(rejected_accounts) == 0:
        message = f"**На все ваши аккаунты был выдан значок {badge.emoji} {badge.name}. Скорее проверяйте!**"
    elif len(given_accounts) > 0 and len(rejected_accounts) > 0:
        message = f"**На все аккаунты был выдан значок {badge.emoji} {badge.name}, которые его еще не получили. Скорее проверяйте!**"
    elif len(given_accounts) == 0 and len(rejected_accounts) > 0:
        message = "**Все аккаунты, привязанные к вашему Discord уже получили этот значок.**"
    elif len(given_accounts) == 0 and len(rejected_accounts) == 0:
        message = "У вас нет ни одного аккаунта в системе News Tools. Скорее подавайте заявки в новостные разделы!"

    given_accounts_announce = ""
    rejected_accounts_announce = ""

    if len(given_accounts) > 0:
        given_accounts_announce = "\n\n**Аккаунты, которые получили значок:**"
        for given_account in given_accounts:
            given_accounts_announce += f"\n- **{given_account.get('guild_name')} — {given_account.get('nickname')}**"

    if len(rejected_accounts) > 0:
        rejected_accounts_announce = "\n\n**Аккаунты, которые уже имеют значок:**"
        for rejected_account in rejected_accounts:
            rejected_accounts_announce += f"\n- **{rejected_account.get('guild_name')} — {rejected_account.get('nickname')}**"

    return await interaction.edit_original_response(
        content=(message + given_accounts_announce + rejected_accounts_announce)
    )


def setup(bot: commands.InteractionBot):
    bot.add_listener(on_badge_giveaway_button_click, name=disnake.Event.button_click)
