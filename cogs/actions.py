import disnake
from disnake.ext import commands
from utils.logger import Logger
from utils.database_orm import methods
from utils.access_checker import command_access_checker
from utils.databases.access_db import AccessDataBase
import datetime
from utils.html.html_generator import (
    html_makers_actions_generator,
    html_pubs_actions_generator,
)
import aiofiles
from random import randint
import os


class Actions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.access_db = AccessDataBase()
        self.methods = methods
        self.log = Logger("cogs.actions.py.log")

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        try:
            await self.access_db.add_command("viewlog_makers")
            await self.access_db.add_command("viewlog_pubs")
        except Exception as error:
            await self.log.critical(f"Не удалось инициализироват команды: {error}.")

    @commands.command(name="viewlog_makers")
    async def view_log_makers(
        self, ctx: commands.Context, date_start: str = None, date_end: str = None
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "viewlog_makers"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /viewlog_makers: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить доступ к команде.**"
                )
                return
            if not access:
                is_owner = await self.bot.is_owner(ctx.author)
                if not is_owner:
                    await ctx.message.add_reaction("❗")
                    await ctx.message.reply(
                        content="**У вас недостаточно прав для выполнения данной команды.**"
                    )
                    return

            data = self.methods.get_all_maker_actions()
            rand_id = randint(9999, 9999999999999999)
            if (not date_start) and (not date_end):
                html_code = await html_makers_actions_generator(data=data)
                async with aiofiles.open(
                    file=f"./tmp/makers-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            elif (date_start) and (not date_end):
                sorted_data = []
                datetime_start = datetime.datetime.fromisoformat(date_start)

                for action in data:
                    action_datetime = action.timestamp
                    if datetime_start <= action_datetime:
                        sorted_data.append(action)

                html_code = await html_makers_actions_generator(
                    data=sorted_data, date_start=date_start
                )
                async with aiofiles.open(
                    file=f"./tmp/makers-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            elif (date_start) and (date_end):
                sorted_data = []
                datetime_start = datetime.datetime.fromisoformat(date_start)
                datetime_end = datetime.datetime.fromisoformat(date_end)
                for action in data:
                    action_datetime = action.timestamp
                    if (datetime_start <= action_datetime) and (
                        datetime_end >= action_datetime
                    ):
                        sorted_data.append(action)

                html_code = await html_makers_actions_generator(
                    data=sorted_data, date_start=date_start, date_end=date_end
                )
                async with aiofiles.open(
                    file=f"./tmp/makers-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            file = disnake.File(
                fp=f"./tmp/makers-logs-{rand_id}.html",
                filename="makers_logs.html",
                spoiler=True,
            )

            await ctx.message.reply(file=file)
            os.remove(f"./tmp/makers-logs-{rand_id}.html")
            await ctx.message.add_reaction("✅")

    @commands.command(name="viewlog_pubs")
    async def view_log_publications(
        self, ctx: commands.Context, date_start: str = None, date_end: str = None
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "viewlog_pubs"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /viewlog_pubs: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить доступ к команде.**"
                )
                return
            if not access:
                is_owner = await self.bot.is_owner(ctx.author)
                if not is_owner:
                    await ctx.message.add_reaction("❗")
                    await ctx.message.reply(
                        content="**У вас недостаточно прав для выполнения данной команды.**"
                    )
                    return

            data = methods.get_all_pub_actions()
            rand_id = randint(9999, 9999999999999999)
            if (not date_start) and (not date_end):
                html_code = await html_pubs_actions_generator(data=data)
                async with aiofiles.open(
                    file=f"./tmp/pubs-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            elif (date_start) and (not date_end):
                sorted_data = []
                datetime_start = datetime.datetime.fromisoformat(date_start)

                for action in data:
                    action_datetime = action.timestamp
                    if datetime_start <= action_datetime:
                        sorted_data.append(action)

                html_code = await html_pubs_actions_generator(
                    data=sorted_data, date_start=date_start
                )
                async with aiofiles.open(
                    file=f"./tmp/pubs-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            elif (date_start) and (date_end):
                sorted_data = []
                datetime_start = datetime.datetime.fromisoformat(date_start)
                datetime_end = datetime.datetime.fromisoformat(date_end)
                for action in data:
                    action_datetime = action.timestamp
                    if (datetime_start <= action_datetime) and (
                        datetime_end >= action_datetime
                    ):
                        sorted_data.append(action)

                html_code = await html_pubs_actions_generator(
                    data=sorted_data, date_start=date_start, date_end=date_end
                )
                async with aiofiles.open(
                    file=f"./tmp/pubs-logs-{rand_id}.html", mode="w", encoding="utf-8"
                ) as file:
                    await file.write(html_code)

            file = disnake.File(
                fp=f"./tmp/pubs-logs-{rand_id}.html",
                filename="pubs_logs.html",
                spoiler=True,
            )

            await ctx.message.reply(file=file)
            os.remove(f"./tmp/pubs-logs-{rand_id}.html")
            await ctx.message.add_reaction("✅")


def setup(bot: commands.Bot):
    bot.add_cog(cog=Actions(bot=bot))
