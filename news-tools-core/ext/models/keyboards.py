import disnake
from disnake.ext import commands
from disnake.ui import View, button, Button
from asyncio import sleep
from os import system

from database.methods import makers as maker_methods, guilds as guild_methods
from ext.models.reusable import *


class ConfirmRoleAction(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @button(label="Подтвердить действие", style=disnake.ButtonStyle.blurple, emoji="✅")
    async def confirm_action(
            self, button: Button, interaction: disnake.MessageInteraction
    ):
        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        if not guild:
            return await interaction.send(
                embed=get_failed_embed("Этот сервер не зарегистрирован в системе."),
                ephemeral=True,
            )

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.send(
                embed=get_failed_embed("У вас недостаточно прав чтобы подтвердить это действие."),
                ephemeral=True
            )
        if not interaction_author.account_status:
            return await interaction.send(
                embed=get_failed_embed("У вас недостаточно прав чтобы подтвердить это действие."),
                ephemeral=True
            )
        if not int(interaction_author.level) >= 3:
            return await interaction.send(
                embed=get_failed_embed("У вас недостаточно прав чтобы подтвердить это действие."),
                ephemeral=True
            )

        await interaction.message.edit(
            content=f"{interaction.message.content}\n`Подтвердил действие` -> {interaction.author.mention}",
            components=[
                Button(
                    style=disnake.ButtonStyle.blurple,
                    label="Подтвердить действие",
                    emoji="✅",
                    disabled=True,
                )
            ],
            allowed_mentions=disnake.AllowedMentions.none(),
        )
        await interaction.message.unpin(
            reason=f"{interaction.author.display_name} подтвердил действие"
        )
        try:
            await interaction.response.send_message()
        except disnake.HTTPException:
            pass


class ConfirmReboot(View):
    def __init__(self, bot: commands.InteractionBot, member: disnake.Member):
        super().__init__(timeout=60)
        self.bot = bot
        self.member = member

    @button(label="Подтвердить", style=disnake.ButtonStyle.danger, emoji="☠️")
    async def confirm(self, button: Button, interaction: disnake.MessageInteraction):
        if not interaction.author.id == self.member.id:
            return await interaction.send(
                embed=get_failed_embed("У вас недостаточно прав для взаимодействия с этой кнопкой."),
                ephemeral=True,
            )

        await interaction.message.edit(
            content="Сервер будет перезагружен через 5 секунд. Перезагрузка займет примерно 3 минуты.",
            view=None,
        )
        await self.bot.change_presence(
            activity=disnake.Activity(
                name="ПЕРЕЗАГРУЗКА", type=disnake.ActivityType.watching
            ),
            status=disnake.Status.idle,
        )
        await sleep(5)
        await interaction.channel.send("Начинаю перезагрузку сервера...")
        return system("sudo reboot")

    @button(label="Отменить", style=disnake.ButtonStyle.green, emoji="❌")
    async def cancel(self, button: Button, interaction: disnake.MessageInteraction):
        if not interaction.author.id == self.member.id:
            return await interaction.send(
                embed=get_failed_embed("У вас недостаточно прав для взаимодействия с этой кнопкой."),
                ephemeral=True
            )

        return await interaction.message.edit(
            content="Вы отменили перезагрузку сервера.", view=None
        )
