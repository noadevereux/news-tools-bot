import disnake
from disnake.ext import commands
from disnake.ui import View, button, Button
from asyncio import sleep
from os import system


class ConfirmRoleAction(View):
    def __init__(self, chief_role: disnake.Role) -> None:
        super().__init__(timeout=None)
        self.chief_role = chief_role

    @button(label="Подтвердить действие", style=disnake.ButtonStyle.blurple, emoji="✅")
    async def confirm_action(
            self, button: Button, interaction: disnake.MessageInteraction
    ):
        if (not self.chief_role in interaction.author.roles) and (
                not interaction.author.guild_permissions.administrator
        ):
            await interaction.send(
                content="**У вас недостаточно прав чтобы подтвердить это действие**",
                ephemeral=True,
            )
            return
        await interaction.message.edit(
            content=f"{interaction.message.content}\n{interaction.author.mention} подтвердил действие.",
            components=[
                Button(
                    style=disnake.ButtonStyle.blurple,
                    label="Подтвердить действие",
                    emoji="✅",
                    disabled=True,
                )
            ],
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
                content="**У вас нет прав для взаимодействия с этой кнопкой.**",
                ephemeral=True
            )

        await interaction.message.edit(
            content="**Сервер будет перезагружен через 5 секунд. Перезагрузка займет примерно 3 минуты.**",
            view=None
        )
        await self.bot.change_presence(
            activity=disnake.Activity(
                name="ПЕРЕЗАГРУЗКА СИСТЕМ",
                type=disnake.ActivityType.watching
            ),
            status=disnake.Status.idle
        )
        await sleep(5)
        await interaction.channel.send("**Начинаю перезагрузку сервера.**")
        return system("sudo reboot")

    @button(label="Отменить", style=disnake.ButtonStyle.green, emoji="❌")
    async def cancel(self, button: Button, interaction: disnake.MessageInteraction):
        if not interaction.author.id == self.member.id:
            return await interaction.send(
                content="**У вас нет прав для взаимодействия с этой кнопкой.**",
                ephemeral=True
            )

        return await interaction.message.edit(
            content="**Вы отменили перезагрузку сервера.**",
            view=None
        )
