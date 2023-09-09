import disnake
from disnake.ext import commands
from disnake.ui import View, button, Button


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
