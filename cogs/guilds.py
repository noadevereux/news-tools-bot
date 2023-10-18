import disnake
from disnake.ext import commands


class Guilds(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot


def setup(bot: commands.InteractionBot):
    bot.add_cog(cog=Guilds(bot=bot))
