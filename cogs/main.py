import disnake
from disnake.ext import commands
from utils.access_checker import command_access_checker

from utils.logger import Logger
from utils.databases.main_db import MainDataBase, MakerActionsTable
from utils.databases.access_db import AccessDataBase
from utils.utilities import *

import datetime
from typing import Literal


class Main(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.db = MainDataBase()
        self.maker_actions_db = MakerActionsTable()
        self.access_db = AccessDataBase()
        self.log = Logger("cogs.main.py.log")

    @commands.Cog.listener(name=disnake.Event.ready)
    async def on_ready(self):
        try:
            await self.db.create_tables()
        except Exception as error:
            await self.log.critical(f"Не удалось инициализировать таблицы: {error}.")

        try:
            await self.access_db.add_command("addmaker")
            await self.access_db.add_command("deactivate")
            await self.access_db.add_command("setnickname")
            await self.access_db.add_command("setdiscord")
            await self.access_db.add_command("setlevel")
            await self.access_db.add_command("setstatus")
            await self.access_db.add_command("profile")
        except Exception as error:
            await self.log.critical(f"Не удалось инициализировать команды: {error}.")

    @commands.command(name="addmaker", usage="addmaker <@ping | ID> <Nick_Name>")
    async def make_maker(
        self, ctx: commands.Context, member: disnake.User, nickname: str
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(ctx.guild, ctx.author, "addmaker")
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /addmaker: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if is_maker_exists:
                timestamp = datetime.datetime.now().isoformat()

                try:
                    await self.db.update_maker(
                        discord_id=member.id, column="account_status", value=1
                    )
                    await self.db.update_maker(
                        discord_id=member.id, column="nickname", value=nickname
                    )
                    await self.db.update_maker(
                        discord_id=member.id,
                        column="appointment_datetime",
                        value=timestamp,
                    )
                    await self.db.update_maker(
                        discord_id=member.id, column="level", value=1
                    )
                    await self.db.update_maker(
                        discord_id=member.id, column="status", value="new"
                    )
                    await self.db.update_maker(
                        discord_id=member.id, column="warns", value=0
                    )
                except Exception as error:
                    await self.log.error(
                        f"Не удалось активировать аккаунт редактора: {error}."
                    )
                    await ctx.message.add_reaction("❗")
                    await ctx.message.reply(
                        content=f"**Произошла непредвиденная ошибка при попытке активировать аккаунт редактора.**",
                    )
                    return

                try:
                    embed = await get_maker_profile(user=member)
                except Exception as error:
                    await self.log.error(
                        f"Произошла ошибка во время инициализации профиля редактора: {error}."
                    )
                    await ctx.message.add_reaction("❗")
                    await ctx.message.reply(
                        content=f"**Произошла ошибка во время инициализации профиля редактора.**",
                    )
                    return

                await ctx.message.add_reaction("✅")
                await ctx.message.reply(
                    content=f"**Вы активировали аккаунт редактора {member.mention} `{nickname}`.**",
                    embed=embed,
                )

                return
            try:
                await self.db.add_maker(discord_id=member.id, nickname=nickname)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке добавить редактора в базу данных: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**{ctx.author.mention}, произошла непредвиденная ошибка при попытке добавить редактора.**",
                )
                return

            try:
                embed = await get_maker_profile(user=member)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка во время инициализации профиля редактора: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка во время инициализации профиля редактора.**",
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы добавили редактора {member.mention} `{nickname}`.**",
            embed=embed,
        )

    @commands.command(name="deactivate", usage="deactivate <@ping | ID>")
    async def deactivate_maker(self, ctx: commands.Context, member: disnake.User):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "deactivate"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /deactivate: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не существует.**"
                )
                return

            try:
                await self.db.deactivate_maker(member.id)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке деактивировать аккаунт редактора: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла непредвиденная ошибка при попытке деактивировать аккаунт редактора.**",
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**{ctx.author.mention}, вы деактивировали аккаунт редактора {member.mention}.**"
        )

    @commands.command(name="profile", usage="profile [@ping | ID]")
    async def maker_profile(self, ctx: commands.Context, member: disnake.User = None):
        if not member:
            member = ctx.author

        async with ctx.typing():
            try:
                access = await command_access_checker(ctx.guild, ctx.author, "profile")
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /profile: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не найден в базе данных.**"
                )
                return

            try:
                embed = await get_maker_profile(user=member)
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка во время инициализации профиля редактора: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка во время инициализации профиля редактора.**",
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(embed=embed)

    @commands.command(name="setdiscord", usage="setdiscord <@ping | ID> <Nick_Name>")
    async def set_nickname(
        self, ctx: commands.Context, member: disnake.User, new_member: disnake.User
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setdiscord"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setdiscord: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не найден.**"
                )
                return

            try:
                is_new_maker_exists = await self.db.is_maker_exists(new_member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if is_new_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {new_member.mention} уже существует.**"
                )
                return

            try:
                await self.db.update_maker(
                    discord_id=member.id, column="discord_id", value=new_member.id
                )
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке обновить дискорд: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка при попытке обновить дискорд.**"
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили редактору {member.mention} дискорд на {new_member.mention}**"
        )

    @commands.command(name="setnickname", usage="setnickname <@ping | ID> <Nick_Name>")
    async def set_nickname(
        self, ctx: commands.Context, member: disnake.User, nickname: str
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setnickname"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setnickname: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не найден.**"
                )
                return

            try:
                await self.db.update_maker(
                    discord_id=member.id, column="nickname", value=nickname
                )
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке обновить никнейм: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка при попытке обновить никнейм.**"
                )
                return

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили редактору {member.mention} никнейм на `{nickname}`**"
        )

    @commands.command(name="setlevel", usage="setlevel <@ping | ID> <level>")
    async def set_level(
        self,
        ctx: commands.Context,
        member: disnake.User,
        level: Literal[-1, 1, 2, 3, 4],
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(ctx.guild, ctx.author, "setlevel")
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setlevel: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не найден.**"
                )
                return

            try:
                await self.db.update_maker(
                    discord_id=member.id, column="level", value=level
                )
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке обновить должность: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка при попытке обновить должность.**"
                )
                return

            level_title = await get_level_title(level)

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили редактору {member.mention} должность на `{level_title}`**"
        )

    @commands.command(name="setstatus", usage="setstatus <@ping | ID> <status>")
    async def set_status(
        self,
        ctx: commands.Context,
        member: disnake.User,
        status: Literal["new", "active", "inactive"],
    ):
        async with ctx.typing():
            try:
                access = await command_access_checker(
                    ctx.guild, ctx.author, "setstatus"
                )
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить доступ к команде /setstatus: {error}."
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
                is_maker_exists = await self.db.is_maker_exists(member.id)
            except Exception as error:
                await self.log.error(
                    f"Не удалось проверить существует ли редактор: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
                )
                return

            if not is_maker_exists:
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Редактор {member.mention} не найден.**"
                )
                return

            try:
                await self.db.update_maker(
                    discord_id=member.id, column="status", value=status
                )
            except Exception as error:
                await self.log.error(
                    f"Произошла ошибка при попытке обновить статус: {error}."
                )
                await ctx.message.add_reaction("❗")
                await ctx.message.reply(
                    content=f"**Произошла ошибка при попытке обновить статус.**"
                )
                return

            status_title = await get_status_title(status)

        await ctx.message.add_reaction("✅")
        await ctx.message.reply(
            content=f"**Вы изменили редактору {member.mention} статус на `{status_title}`**"
        )

    # @commands.command(name = "setcolor", usage = "setcolor <@ping | ID> <color>")
    # @commands.has_role(CHIEF_ROLE_ID)
    # async def set_color(
    #     self,
    #     ctx: commands.Context,
    #     member: disnake.User,
    #     color: str
    # ):
    #     async with ctx.typing():

    #         if color.startswith("#"):
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content="Напишите цвет в формате HEX без знака \"#\" в начале."
    #             )
    #             return

    #         try:
    #             is_maker_exists = await self.db.is_maker_exists(member.id)
    #         except Exception as error:
    #             await self.log.error(f"Не удалось проверить существует ли редактор: {error}.")
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
    #             )
    #             return

    #         if not is_maker_exists:
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content = f"**{ctx.author.mention}, редактор {member.mention} не найден.**"
    #             )
    #             return

    #         try:
    #             await self.db.update_maker(
    #                 discord_id = member.id,
    #                 column = "color",
    #                 value = color
    #             )
    #         except Exception as error:
    #             await self.log.error(f"Произошла ошибка при попытке обновить цвет: {error}.")
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content = f"**{ctx.author.mention}, произошла ошибка при попытке обновить цвет.**"
    #             )
    #             return

    #     await ctx.message.add_reaction("✅")
    #     await ctx.message.reply(
    #         content = f"**{ctx.author.mention}, вы изменили редактору {member.mention} цвет на `#{color}`**"
    #     )

    # @commands.command(name = "seticon", usage = "seticon <@ping | ID> <link>")
    # @commands.has_role(CHIEF_ROLE_ID)
    # async def set_icon(
    #     self,
    #     ctx: commands.Context,
    #     member: disnake.User,
    #     link: str
    # ):
    #     async with ctx.typing():

    #         try:
    #             is_maker_exists = await self.db.is_maker_exists(member.id)
    #         except Exception as error:
    #             await self.log.error(f"Не удалось проверить существует ли редактор: {error}.")
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content=f"**Произошла ошибка, не удалось проверить существует ли редактор.**"
    #             )
    #             return

    #         if not is_maker_exists:
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content = f"**{ctx.author.mention}, редактор {member.mention} не найден.**"
    #             )
    #             return

    #         try:
    #             await self.db.update_maker(
    #                 discord_id = member.id,
    #                 column = "icon_link",
    #                 value = link
    #             )
    #         except Exception as error:
    #             await self.log.error(f"Произошла ошибка при попытке обновить ссылку на аватар: {error}.")
    #             await ctx.message.add_reaction("❗")
    #             await ctx.message.reply(
    #                 content = f"**{ctx.author.mention}, произошла ошибка при попытке обновить ссылку на аватар.**"
    #             )
    #             return

    #     await ctx.message.add_reaction("✅")
    #     await ctx.message.reply(
    #         content = f"**{ctx.author.mention}, вы изменили редактору {member.mention} ссылку на аватарку на `{link}`**"
    #     )


def setup(bot: commands.Bot):
    bot.add_cog(Main(bot=bot))
