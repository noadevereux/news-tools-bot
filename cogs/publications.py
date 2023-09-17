from typing import Literal
import disnake
from disnake.ext import commands
from utils.logger import Logger
from utils.databases.access_db import AccessDataBase
from utils.database_orm import methods
from utils.access_checker import command_access_checker
from utils.utilities import date_validator, get_publication_profile, get_status_title


class Publications(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.methods = methods
        self.log = Logger("cogs.publications.py.log")
        self.access_db = AccessDataBase()

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        try:
            await self.access_db.add_command("createpub")
            await self.access_db.add_command("deletepub")
            await self.access_db.add_command("pubprofile")
            await self.access_db.add_command("setpub_id")
            await self.access_db.add_command("setpub_date")
            await self.access_db.add_command("setpub_maker")
            await self.access_db.add_command("setpub_status")
            await self.access_db.add_command("setpub_amount")
            await self.access_db.add_command("setpub_infocreator")
            await self.access_db.add_command("setpub_salarypayer")
        except Exception as error:
            await self.log.critical(f"Не удалось инициализировать команды: {error}.")

    @commands.command(name="createpub")
    async def create_pub(self, ctx: commands.Context, id: int):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "createpub"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /createpub: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером уже существует.**"
                )
                return

            try:
                self.methods.add_publication(publication_id=id)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке добавить выпуск в БД: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка при попытке добавить выпуск.**"
                )
                return

            try:
                embed = await get_publication_profile(publication_id=id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось инициализировать информацию о выпуске: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось инициализировать информацию о выпуске.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="createpub",
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(content="**Вы успешно создали выпуск**", embed=embed)

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="deletepub")
    async def delete_pub(self, ctx: commands.Context, id: int):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "deletepub"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /deletepub: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.delete_publication(publication_id=id)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке удалить выпуск из БД: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка при попытке удалить выпуск.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id, made_by=made_by, action="deletepub", meta=id
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(content=f"**Вы успешно удалили выпуск #{id}**")

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="pubprofile")
    async def pub_profile(self, ctx: commands.Context, id: int):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "pubprofile"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /pubprofile: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                embed = await get_publication_profile(publication_id=id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось инициализировать информацию о выпуске: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось инициализировать информацию о выпуске.**"
                )
                return

            await ctx.message.add_reaction("✅")
            await ctx.message.reply(embed=embed)

    @commands.command(name="setpub_id")
    async def set_pub_id(self, ctx: commands.Context, id: int, new_id: int):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_id"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_id: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                is_new_publication_exists = self.methods.is_publication_exists(
                    publication_id=new_id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if is_new_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером уже существует.**"
                )
                return

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="publication_number", value=new_id
                )
            except Exception as error:
                await self.log.error(f"Не удалось обновить ID выпуска: {error}.")
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить ID выпуска.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_id",
                    meta=f"[{id}, {new_id}]",
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили номер выпуска #{id}. Его новый номер: #{new_id}.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_date")
    async def set_pub_date(self, ctx: commands.Context, id: int, date: str):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_date"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_date: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            is_date_valid = await date_validator(date_string=date)

            if not is_date_valid:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Неверный формат даты. Укажите дату в формате `гггг-мм-дд`.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="date", value=date
                )
            except Exception as error:
                await self.log.error(f"Не удалось обновить дату выпуска: {error}.")
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить дату выпуска.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_date",
                    meta=date,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили дату выпуска #{id} на {date}.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_maker")
    async def set_pub_maker(self, ctx: commands.Context, id: int, maker: disnake.User):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_maker"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_maker: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                maker_db = self.methods.get_maker(discord_id=maker.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not maker_db:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Редактор не существует в базе данных**"
                )
                return

            if maker_db.account_status == False:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Аккаунт редактора деактивирован, невозможно указать его в качестве исполнителя.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="maker_id", value=maker_db.id
                )
            except Exception as error:
                await self.log.error(f"Не удалось обновить редактора выпуска: {error}.")
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить редактора выпуска.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_maker",
                    meta=maker_db.id,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили редактора выпуска #{id} на <@{maker_db.discord_id}>.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_status")
    async def set_pub_status(
        self,
        ctx: commands.Context,
        id: int,
        status: Literal["in_process", "completed", "failed"],
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_status"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_status: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="status", value=status
                )
            except Exception as error:
                await self.log.error(f"Не удалось обновить статус выпуска: {error}.")
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить статус выпуска.**"
                )
                return

            status_title = await get_status_title(status_kw=status)

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_status",
                    meta=status,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили статус выпуска #{id} на `{status_title}`.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_amount")
    async def set_pub_amount(
        self,
        ctx: commands.Context,
        id: int,
        amount: int,
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_amount"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_amount: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="amount_dp", value=amount
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось обновить зарплату за выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить зарплату за выпуск.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_amount",
                    meta=amount,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили зарплату за выпуск #{id} на {amount} DP.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_infocreator")
    async def set_pub_infocreator(
        self, ctx: commands.Context, id: int, creator: disnake.User
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_infocreator"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_infocreator: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                creator_db = self.methods.get_maker(discord_id=creator.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not creator_db:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Редактор не существует в базе данных**"
                )
                return

            if not creator_db.account_status:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Аккаунт редактора деактивирован, невозможно указать его в качестве автора информации.**"
                )
                return

            if int(creator_db.level) < 2:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**У редактора недостаточно прав для того чтобы быть автором информации.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id,
                    column_name="information_creator_id",
                    value=creator_db.id,
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось обновить автора информации к выпуску: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить автора информации к выпуску.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_infocreator",
                    meta=creator_db.id,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили автора информации к выпуску #{id} на <@{creator_db.discord_id}>.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )

    @commands.command(name="setpub_salarypayer")
    async def set_pub_salarypayer(
        self, ctx: commands.Context, id: int, payer: disnake.User
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setpub_salarypayer"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setpub_salarypayer: {error}."
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
                is_publication_exists = self.methods.is_publication_exists(
                    publication_id=id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли выпуск.**"
                )
                return

            if not is_publication_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Выпуск с таким номером не существует.**"
                )
                return

            try:
                payer_db = self.methods.get_maker(discord_id=payer.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not payer_db:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Редактор не существует в базе данных**"
                )
                return

            if payer_db.account_status == False:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Аккаунт редактора деактивирован, невозможно указать его в качестве человека, который выплатил зарплату за выпуск.**"
                )
                return

            if int(payer_db.level) < 2:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**У редактора недостаточно прав для того чтобы быть человеком, который выплатил зарплату за выпуск.**"
                )
                return

            try:
                self.methods.update_publication(
                    publication_id=id, column_name="salary_payer_id", value=payer_db.id
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось обновить человека, который выплатил зарплату за выпуск: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content="**Произошла ошибка, не удалось обновить человека, который выплатил зарплату за выпуск.**"
                )
                return

            try:
                made_by = self.methods.get_maker(discord_id=ctx.author.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось найти исполнителя команды в базе данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, вас не удалось найти в базе данных.**"
                )
                return

            if not made_by:
                made_by = None
            else:
                made_by = made_by.id

            try:
                publication = self.methods.get_publication(publication_id=id)
            except Exception as error:
                await self.log.error(f"Не удалось получить выпуск: {error}.")
                await ctx.message.add_reaction("❗")
                return await ctx.message.reply(
                    content="**Не удалось инициализировать выпуск.**"
                )

            try:
                self.methods.add_pub_action(
                    pub_id=publication.id,
                    made_by=made_by,
                    action="setpub_salarypayer",
                    meta=payer_db.id,
                )
                action_written_success = True
            except Exception as error:
                await self.log.error(
                    f"Не удалось записать действие с публикацией: {error}."
                )
                action_written_success = False

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили человека, который выплатил зарплату за выпуск #{id} на <@{payer_db.discord_id}>.**"
        )

        if not action_written_success:
            await ctx.message.reply(
                content="**Произошла ошибка во время записи действия в лог.**"
            )


def setup(bot: commands.Bot):
    bot.add_cog(cog=Publications(bot=bot))
