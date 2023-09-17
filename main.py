from asyncio import run
import disnake
from disnake.ext import commands
import os
from config import PREFIX, TOKEN
from utils.logger import Logger
from utils.database_orm.database import engine
from utils.database_orm.orm_models import Base
from utils.databases.access_db import AccessDataBase

bot = commands.Bot(
    command_prefix=PREFIX,
    help_command=None,
    intents=disnake.Intents.all(),
)

access_db = AccessDataBase()

log = Logger("main.py.log")


@bot.command(name="loadcog")
@commands.is_owner()
async def load_cog(ctx: commands.Context, extension: str):
    # Загрузка кога
    try:
        bot.load_extension(name=f"cogs.{extension}")
        await ctx.message.add_reaction("✅")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} загружен.", delete_after=5
        )
    except commands.errors.ExtensionNotFound:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} не найден.", delete_after=5
        )
    except commands.errors.ExtensionAlreadyLoaded:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} уже загружен.",
            delete_after=5,
        )
    except Exception as error:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, произошла ошибка при загрузке кога {extension}, информация записана в лог."
        )
        await log.error(error)
        print(error)


@bot.command(name="reloadcog")
@commands.is_owner()
async def reload_cog(ctx: commands.Context, extension: str):
    # Перезагрузка кога
    try:
        bot.reload_extension(name=f"cogs.{extension}")
        await ctx.message.add_reaction("✅")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} перезагружен.",
            delete_after=5,
        )
    except commands.errors.ExtensionNotLoaded:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} не загружен.",
            delete_after=5,
        )
    except commands.errors.ExtensionNotFound:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} не найден.", delete_after=5
        )
    except Exception as error:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, произошла ошибка при перезагрузке кога {extension}, информация записана в лог."
        )
        await log.error(error)
        print(error)


@bot.command(name="unloadcog")
@commands.is_owner()
async def unload_cog(ctx: commands.Context, extension: str):
    # Отгрузка кога
    try:
        bot.unload_extension(name=f"cogs.{extension}")
        await ctx.message.add_reaction("✅")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} отгружен.", delete_after=5
        )
    except commands.errors.ExtensionNotLoaded:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} не загружен.",
            delete_after=5,
        )
    except commands.errors.ExtensionNotFound:
        await ctx.message.add_reaction("❗")
        await ctx.send(
            content=f"{ctx.author.mention}, ког {extension} не найден.", delete_after=5
        )


@bot.listen(name="on_ready")
async def on_ready():
    print(f"[INFO] {bot.user} запущен.")
    await log.info("Запущена новая сессия.")


if __name__ == "__main__":
    run(access_db.create_table())
    Base.metadata.create_all(bind=engine)
    for file in os.listdir("cogs"):
        if (file.endswith(".py")) and (not file.startswith(".")):
            try:
                bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as error:
                print(error)
    bot.run(TOKEN)
