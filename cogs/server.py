import disnake
from disnake.ext import commands
from config import DEV_GUILDS
import os
from asyncio import sleep
from utils.models.keyboards import ConfirmReboot


class Server(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name="server", description="[DEV] Управление сервером", guild_ids=DEV_GUILDS)
    @commands.is_owner()
    async def server(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @server.sub_command(name="reboot", description="[DEV] Перезагрузить сервер")
    async def server_reboot(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        return await interaction.send(
            content=f"**Вы уверены что хотите перезагрузить сервер?**",
            view=ConfirmReboot(bot=self.bot, member=interaction.author)
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(cog=Server(bot=bot))
