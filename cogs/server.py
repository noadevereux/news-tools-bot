import disnake
from disnake.ext import commands
from config import DEV_GUILDS
import os
from asyncio import sleep


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
        await interaction.send(
            content=f"**Сервер будет перезагружен через 5 секунд. Примерно время перезагрузки составит 5 минут.**"
        )
        await self.bot.change_presence(
            activity=disnake.Activity(
                name="ПЕРЕЗАГРУЗКА СИСТЕМ",
                type=disnake.ActivityType.listening
            ),
            status=disnake.Status.idle
        )
        await sleep(5.0)
        return os.system("sudo reboot")


def setup(bot: commands.InteractionBot):
    bot.add_cog(cog=Server(bot=bot))
