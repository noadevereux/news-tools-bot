import disnake
from disnake.ext import commands
from ext.logger import Logger
from datetime import datetime

from ext.models.exceptions import *


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.error_handler.py.log")

    @commands.Cog.listener(name=disnake.Event.slash_command_error)
    async def on_slash_command_error(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            error: commands.CommandError,
    ):
        error_uid = await self.log.error(log_message=error, exc=error)

        has_been_responded = interaction.response.is_done()
        if not has_been_responded:
            await interaction.response.defer(ephemeral=True)

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
            colour=disnake.Colour.red(),
        )

        if interaction.guild and interaction.guild.icon:
            embed.set_author(name=error_uid, icon_url=interaction.guild.icon.url)
        else:
            embed.set_author(name=error_uid)

        if isinstance(error, commands.errors.GuildNotFound):
            return await interaction.edit_original_response(
                content=f"**Сервер с ID `{error.argument}` не найден. Возможно бот не добавлен на этот сервер или его не существует.**"
            )
        elif isinstance(error, commands.NotOwner):
            return await interaction.edit_original_response(
                content="**Эта команда доступна только разработчикам.**"
            )
        elif isinstance(error, commands.LargeIntConversionFailure):
            return await interaction.edit_original_response(
                content=f"**Один из параметров принимает только числовые значения, но получено `{error.argument}`.**"
            )
        elif isinstance(error, GuildNotExists):
            return await interaction.edit_original_response(
                content="**Этот сервер не зарегистрирован или не активен. Использовать команды на нем невозможно.**"
            )
        elif isinstance(error, CommandCalledInDM):
            return await interaction.edit_original_response(
                content="**Эту команду нельзя использовать в личных сообщениях.**"
            )
        elif isinstance(error, GuildNotAdmin):
            return await interaction.edit_original_response(
                content="**Этот сервер не обладает административным доступом для доступа к этой команде.**"
            )
        elif isinstance(error, UserNotExists):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для использования этой команды.**"
            )
        elif isinstance(error, UserNotAdmin):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для использования этой команды.**"
            )
        else:
            return await interaction.edit_original_response(embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(ErrorHandler(bot=bot))
