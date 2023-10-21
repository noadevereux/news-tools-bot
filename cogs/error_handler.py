import disnake
from disnake.ext import commands
from ext.logger import Logger
from datetime import datetime


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
        error_uid = await self.log.error(f"{error}")

        has_been_responded = interaction.response.is_done()

        embed = disnake.Embed(
            title="Произошла ошибка",
            description=f"""\
**Во время выполнения команды `/{interaction.application_command.qualified_name}` произошла непредвиденная ошибка.**

**Уникальный идентификатор ошибки:**
```
{error_uid}
```

**Сообщите разработчикам об ошибке приложив её уникальный идентификатор, чтобы они смогли решить её.**

**Приносим свои извинения за доставленные неудобства.**
""",
            timestamp=datetime.now(),
            colour=disnake.Colour.red()
        )

        embed.set_author(name=error_uid, icon_url=(interaction.guild.icon.url if not None else None))

        if isinstance(error, commands.errors.GuildNotFound):
            if not has_been_responded:
                await interaction.response.defer(ephemeral=True)
            return await interaction.edit_original_response(
                content="**Сервер с указанным ID не найден. Возможно бот не добавлен на этот сервер или его не существует.**"
            )
        elif isinstance(error, commands.NotOwner):
            if not has_been_responded:
                await interaction.response.defer(ephemeral=True)
            return await interaction.edit_original_response(
                content="**Эта команда доступна только разработчикам.**"
            )
        else:
            if not has_been_responded:
                await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_response(
                embed=embed
            )


def setup(bot: commands.InteractionBot):
    bot.add_cog(ErrorHandler(bot=bot))
