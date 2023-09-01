from json import loads
from utils.errors import IncorrectCommandName
from utils.logger import Logger
import disnake
from disnake.ext import commands
from utils.access_checker import command_access_checker
from utils.databases.access_db import AccessDataBase


class AccessSetting(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.db = AccessDataBase()
        self.log = Logger("cogs.access_setting.py.log")

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        await self.db.create_table()
        await self.db.add_command("access")
        await self.db.add_command("setaccess")
        await self.db.add_command("revokeaccess")

    @commands.command(name="access")
    async def access_list(self, ctx: commands.Context):
        async with ctx.typing():
            try:
                access = await command_access_checker(ctx.guild, ctx.author, "access")
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /access: {error}."
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

            data = await self.db.get_all()

            description = ""

            for command in data:
                command_name = f"/{command[1]}"
                roles = ""
                roles_list = loads(command[2])
                for role in roles_list:
                    roles += f"<@&{role}> "

                if roles == "":
                    roles = "`Доступ закрыт`"

                # description += f"# ```↓ {command_name}```\n### {roles}\n"
                description += f"**{command_name}** -> {roles}\n\n"

            if description == "":
                description = "### ```В боте не зарегистрировано ни одной команды (как так вышло...)```"

            embed = disnake.Embed(
                title="Настройки доступа к командам NewsTools",
                color=0x2B2D31,
                description=description,
            )
            embed.set_thumbnail(url="https://i.imgur.com/kDWoqDR.png")

        await ctx.message.add_reaction("✅")
        await ctx.send(embed=embed)

    @commands.command(name="setaccess")
    async def set_access(
        self, ctx: commands.Context, command_name: str, *roles: disnake.Role
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setaccess"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setaccess: {error}."
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

            role_ids = [role.id for role in roles]

            try:
                await self.db.set_access(command_name, *role_ids)
            except IncorrectCommandName:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Команда `/{command_name}` не найдена.**"
                )
                return
            except Exception as error:
                await self.log.error(
                    f"Не удалось обновить настройки команды /{command_name}: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось обновить настройки для команды.**"
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы успешно обновили права доступа для команды `/{command_name}`.**"
        )

    @commands.command(name="revokeaccess")
    async def revoke_access(self, ctx: commands.Context, command_name: str):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "revokeaccess"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /revokeaccess: {error}."
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

            try:
                await self.db.set_access(command_name, [])
            except IncorrectCommandName:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Команда `/{command_name}` не найдена.**"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось отозвать права доступа для команды /{command_name}: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось отозвать права доступа для команды.**"
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы успешно отозвали все права доступа для команды `/{command_name}`.**"
        )


def setup(bot: commands.Bot):
    bot.add_cog(cog=AccessSetting(bot=bot))
