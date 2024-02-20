import os
import asyncio
import disnake
from disnake.ext import commands, tasks

from config import TOKEN, DEV_GUILDS
from ext.database.models import create_tables
from ext.logger import Logger

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
            content=f"Модуль {extension} не найден."
        )
    except commands.errors.ExtensionAlreadyLoaded:
        return await interaction.edit_original_response(
            content=f"Модуль {extension} уже загружен."
        )
    except Exception as exception:
        await interaction.edit_original_response(
            content=f"Произошла ошибка при загрузке модуля {extension}, информация записана в лог."
        )
        return await log.error(exception)

    return await interaction.edit_original_response(
        content=f"Модуль {extension} загружен."
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
            content=f"Модуль {extension} не загружен."
        )
    except commands.errors.ExtensionNotFound:
        return await interaction.edit_original_response(
            content=f"Модуль {extension} не найден."
        )
    except Exception as exception:
        await interaction.edit_original_response(
            content=f"Произошла ошибка при перезагрузке модуля {extension}, информация записана в лог."
        )
        return await log.error(exception)

    return await interaction.edit_original_response(
        content=f"Модуль {extension} перезагружен."
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
            content=f"Модуль {extension} не загружен."
        )
    except commands.errors.ExtensionNotFound:
        return await interaction.edit_original_response(
            content=f"Модуль {extension} не найден."
        )

    return await interaction.edit_original_response(
        content=f"Модуль {extension} отгружен."
    )


@bot.listen(name="on_ready")
async def on_ready():
    # await create_db_tables.start()
    await log.info("Запущена новая сессия.")
    await bot.change_presence(
        activity=disnake.Activity(
            name="news-tools.ru | v1.1", type=disnake.ActivityType.playing
        ),
        status=disnake.Status.online,
    )


# @tasks.loop(count=1)
# async def create_db_tables():
#     await create_tables()


async def main():
    for file in os.listdir("cogs"):
        if (file.endswith(".py")) and (not file.startswith(".")):
            try:
                bot.load_extension(f"cogs.{file[:-3]}")
            except Exception as error:
                print(error)
    try:
        await bot.start(TOKEN)
    except RuntimeError:
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
