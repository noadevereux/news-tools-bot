import disnake
from disnake.ext import commands
from ext.logger import Logger


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.error_handler.py.log")

    @commands.Cog.listener(name=disnake.Event.slash_command_error)
    async def on_slash_command_error(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            error: commands.CommandError
    ):
        if isinstance(error, commands.errors.GuildNotFound):
            print(1)
            return await interaction.send(
                content="**Сервер с указанным ID не найден. Возможно бот не добавлен на этот сервер или его не существует.**",
                ephemeral=True
            )
        else:
            await self.log.error(f"{error}")


def setup(bot: commands.InteractionBot):
    bot.add_cog(ErrorHandler(bot=bot))
