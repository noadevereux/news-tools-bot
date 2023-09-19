from disnake.ext import commands, tasks

from api.main import start_server


class API(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        self.start_server.start()

    @tasks.loop(count=1)
    async def start_server(self) -> None:
        await start_server(self.bot)


def setup(bot: commands.Bot):
    bot.add_cog(API(bot))
