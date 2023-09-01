import disnake
from disnake.ext import commands
from utils.databases.main_db import MakerActionsTable, PubsActionsTable
from utils.logger import Logger
from utils.access_checker import command_access_checker
from utils.databases.access_db import AccessDataBase


class Actions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.makers_db = MakerActionsTable()
        self.pubs_db = PubsActionsTable()
        self.access_db = AccessDataBase()
        self.log = Logger("cogs.actions.py.log")

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        try:
            await self.makers_db.create_tables()
            await self.pubs_db.create_tables()
        except Exception as error:
            await self.log.critical(
                f"Не удалось инициализировать таблицы actions: {error}."
            )


def setup(bot: commands.Bot):
    bot.add_cog(cog=Actions(bot=bot))
