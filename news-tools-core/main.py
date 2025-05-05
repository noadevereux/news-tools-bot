import datetime
import os
import asyncio
import disnake
from disnake.ext import commands, tasks

from config import TOKEN, DEV_GUILDS, temp, MYSQL_USER, MYSQL_PASSWORD
from ext.logger import Logger
from ext.models.reusable import *

from database.database import SessionManager

bot = commands.InteractionBot(intents=disnake.Intents.all())

log = Logger("main.py.log")


@bot.slash_command(
    name="cog", description="[DEV] Управление модулями бота", guild_ids=DEV_GUILDS
)
@commands.is_owner()
async def cog(interaction: disnake.ApplicationCommandInteraction):
    pass


@cog.sub_command(name="load", description="[DEV] Загрузить модуль бота")
async def cog_load(
        interaction: disnake.ApplicationCommandInteraction,
        extension: str = commands.Param(name="module", description="Название модуля"),
):
    await interaction.response.defer(ephemeral=True)

    try:
        bot.load_extension(name=f"cogs.{extension}")
    except commands.errors.ExtensionNotFound:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** не найден.")
        )
    except commands.errors.ExtensionAlreadyLoaded:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** уже загружен.")
        )
    except Exception as exception:
        await interaction.edit_original_response(
            embed=get_failed_embed(f"Произошла ошибка при загрузке модуля **{extension}**, информация записана в лог.")
        )
        return await log.error(exception)

    return await interaction.edit_original_response(
        embed=get_success_embed(f"Модуль **{extension}** загружен.")
    )


@cog.sub_command(name="reload", description="[DEV] Перезагрузить модуль бота")
async def cog_reload(
        interaction: disnake.ApplicationCommandInteraction,
        extension: str = commands.Param(name="module", description="Название модуля"),
):
    await interaction.response.defer(ephemeral=True)

    try:
        bot.reload_extension(name=f"cogs.{extension}")
    except commands.errors.ExtensionNotLoaded:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** не загружен.")
        )
    except commands.errors.ExtensionNotFound:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** не найден.")
        )
    except Exception as exception:
        await interaction.edit_original_response(
            embed=(f"Произошла ошибка при перезагрузке модуля **{extension}**, информация записана в лог.")
        )
        return await log.error(exception)

    return await interaction.edit_original_response(
        embed=get_success_embed(f"Модуль **{extension}** перезагружен.")
    )


@cog.sub_command(name="unload", description="[DEV] Выгрузить модуль бота")
async def cog_unload(
        interaction: disnake.ApplicationCommandInteraction,
        extension: str = commands.Param(name="module", description="Название модуля"),
):
    await interaction.response.defer(ephemeral=True)

    try:
        bot.unload_extension(name=f"cogs.{extension}")
    except commands.errors.ExtensionNotLoaded:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** не загружен.")
        )
    except commands.errors.ExtensionNotFound:
        return await interaction.edit_original_response(
            embed=get_failed_embed(f"Модуль **{extension}** не найден.")
        )

    return await interaction.edit_original_response(
        embed=get_success_embed(f"Модуль **{extension}** отгружен.")
    )


@bot.listen(name="on_ready")
async def on_ready():
    # await create_db_tables.start()
    await log.info("Запущена новая сессия.")
    temp["startup_time"] = datetime.datetime.now()
    await change_presence.start()


# @tasks.loop(count=1)
# async def create_db_tables():
#     await create_tables()

@tasks.loop(seconds=3)
async def change_presence():
    if not temp.get("current_presence"):
        temp["current_presence"] = 1
    
    match temp["current_presence"]:
        case 1:
            await bot.change_presence(
                    activity=disnake.Activity(
                        name="v1.4", type=disnake.ActivityType.watching
                    ),
                    status=disnake.Status.online,
                )
            
            temp["current_presence"] = 2

        case _:
            await bot.change_presence(
                    activity=disnake.Activity(
                        name="https://github.com/noadevereux/news-tools-bot", type=disnake.ActivityType.watching
                    ),
                    status=disnake.Status.online,
                )
            
            temp["current_presence"] = 1


async def load_cogs():
    for file in os.listdir("cogs"):
        if (file.endswith(".py")) and (not file.startswith(".") and "__" not in file):
            try:
                bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as error:
                print(error)


async def main():
    await SessionManager().startup()

    await load_cogs()

    await bot.start(TOKEN)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
