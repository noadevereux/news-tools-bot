import datetime
import os
import asyncio
import disnake
from disnake.ext import commands

from config import TOKEN, DEV_GUILDS, temp
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
    await bot.change_presence(
        activity=disnake.Activity(
            name="news-tools.ru | v1.3", type=disnake.ActivityType.playing
        ),
        status=disnake.Status.online,
    )

    temp["startup_time"] = datetime.datetime.now()


# @tasks.loop(count=1)
# async def create_db_tables():
#     await create_tables()


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
