import datetime

from disnake.ext import commands
from sqlalchemy.exc import IntegrityError

from utils.database_orm import methods
from utils.databases.access_db import AccessDataBase
from utils.logger import Logger
from utils.utilities import *


class Main(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.access_db = AccessDataBase()
        self.log = Logger("cogs.main.py.log")

    @commands.Cog.listener(name=disnake.Event.ready)
    async def on_ready(self):
        try:
            await self.access_db.add_command("addmaker")
            await self.access_db.add_command("deactivate")
            await self.access_db.add_command("setnickname")
            await self.access_db.add_command("setdiscord")
            await self.access_db.add_command("setlevel")
            await self.access_db.add_command("setstatus")
            await self.access_db.add_command("warn")
            await self.access_db.add_command("unwarn")
            await self.access_db.add_command("profile")
        except Exception as error:
            await self.log.critical(f"Не удалось инициализировать команды: {error}.")

    @commands.slash_command(name="maker", description="Управление редактором")
    async def maker(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @maker.sub_command(name="register", description="Зарегистрировать редактора в системе")
    async def maker_register(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            nickname: str = commands.Param(name="nickname", description="Никнейм редактора")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if maker and (not maker.account_status):
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе, используйте `/maker activate` чтобы активировать его аккаунт.**"
            )

        elif maker and maker.account_status:
            return await interaction.edit_original_response(
                content="**Редактор уже зарегистрирован в системе и его аккаунт активен.**"
            )

        try:
            methods.add_maker(discord_id=member.id, nickname=nickname)
        except IntegrityError:
            return await interaction.edit_original_response(
                content="**Редактор с указанным никнеймом уже существует.**"
            )

        maker = methods.get_maker(member.id)

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="addmaker",
            meta=nickname,
        )

        embed = await get_maker_profile(member)

        return await interaction.edit_original_response(
            content=f"**Вы зарегистрировали редактора {member.mention} `{nickname}` в системе.**",
            embed=embed
        )

    @maker.sub_command(name="activate", description="Активировать аккаунт редактора")
    async def maker_activate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            nickname: str = commands.Param(name="nickname", description="Никнейм редактора")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе. Используйте `/maker register` чтобы зарегистрировать редактора.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.account_status:
            return await interaction.edit_original_response(
                content="**Аккаунт редактора итак активен.**"
            )

        timestamp = datetime.datetime.now().isoformat()

        methods.update_maker(
            discord_id=member.id,
            column_name="account_status",
            value=True
        )

        if not maker.nickname == nickname:
            try:
                methods.update_maker(
                    discord_id=member.id,
                    column_name="nickname",
                    value=nickname
                )
            except IntegrityError:
                return await interaction.edit_original_response(
                    content="**Указанный никнейм занят, выберите другой.**"
                )

        methods.update_maker(
            discord_id=member.id,
            column_name="appointment_datetime",
            value=timestamp
        )

        if not maker.level == "1":
            methods.update_maker(
                discord_id=member.id,
                column_name="level",
                value="1"
            )

        if not maker.status == "new":
            methods.update_maker(
                discord_id=member.id,
                column_name="status",
                value="new"
            )

        if not maker.warns == 0:
            methods.update_maker(
                discord_id=member.id,
                column_name="warns",
                value=0
            )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="addmaker",
            meta=nickname
        )

        embed = await get_maker_profile(member)

        return await interaction.edit_original_response(
            content=f"**Вы активировали аккаунт редактора {member.mention} `{nickname}`.**",
            embed=embed
        )

    @maker.sub_command(name="deactivate", description="Деактивировать аккаунт редактора")
    async def maker_deactivate(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            reason: str = commands.Param(name="reason", description="Причина деактивации")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif not maker.account_status:
            return await interaction.edit_original_response(
                content="**Аккаунт редактора итак деактивирован.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="account_status",
            value=False
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="deactivate",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы деактивировали аккаунт редактора {member.mention} `{maker.nickname}`. Причина: {reason}.**"
        )

    @commands.slash_command(name="profile", description="Посмотреть профиль редактора")
    async def maker_profile(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(default=None, name="maker",
                                                                   description="Редактор или его Discord ID")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )
        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        if not member:
            member = interaction.author

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Пользователь, которого вы указали, не зарегистрирован в системе.**"
            )

        embed = await get_maker_profile(member)

        return await interaction.edit_original_response(
            embed=embed
        )

    @maker.sub_command(name="setdiscord", description="Изменить редактору Discord")
    async def maker_setdiscord(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker", description="Редактор или его ID"),
            new_member: disnake.User | disnake.Member = commands.Param(name="user",
                                                                       description="Пользователь или его ID")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        if member.id == new_member.id:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, вы указали двух одинаковых пользователей.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        if methods.is_maker_exists(new_member.id):
            return await interaction.edit_original_response(
                content="**Пользователь, которого вы указали, уже привязан к какому-то аккаунту.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="discord_id",
            value=new_member.id
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setdiscord",
            meta=str(new_member.id)
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили Discord редактору с ID `{maker.id}` с {member.mention} на {new_member.mention}.**"
        )

    @maker.sub_command(name="setnickname", description="Изменить никнейм редактора")
    async def maker_setnickname(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            nickname: str = commands.Param(name="nickname", description="Никнейм")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.nickname == nickname:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, никнейм, который вы указали, итак принадлежит редактору.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="nickname",
            value=nickname
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setnickname",
            meta=nickname
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили никнейм редактора {member.mention} с `{maker.nickname}` на `{nickname}`.**"
        )

    @maker.sub_command(name="setlevel", description="Изменить должность редактора")
    async def maker_setlevel(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            level: str = commands.Param(
                name="level",
                description="Должность",
                choices=[
                    disnake.OptionChoice(name="Куратор", value="4"),
                    disnake.OptionChoice(name="Главный редактор", value="3"),
                    disnake.OptionChoice(name="Заместитель главного редактора", value="2"),
                    disnake.OptionChoice(name="Редактор", value="1"),
                    disnake.OptionChoice(name="Хранитель", value="-1")
                ]
            )
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) <= int(level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**Вы не можете установить редактору должность, которая равна или выше вашей.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.level == level:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, должность, которую вы указали, итак принадлежит редактору.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="level",
            value=level
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setlevel",
            meta=level
        )

        level_title = await get_level_title(int(level))

        return await interaction.edit_original_response(
            content=f"**Вы назначили редактору {member.mention} `{maker.nickname}` должность `{level_title}`.**"
        )

    @maker.sub_command(name="setstatus", description="Изменить статус редактора")
    async def maker_setstatus(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            status: str = commands.Param(
                name="status",
                description="Статус",
                choices=[
                    disnake.OptionChoice(name="Активен", value="active"),
                    disnake.OptionChoice(name="Неактивен", value="inactive"),
                    disnake.OptionChoice(name="На испытательном сроке", value="new")
                ]
            )
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        elif maker.status == status:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, статус, который вы указали, уже установлен редактору.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="status",
            value=status
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="setstatus",
            meta=status
        )

        status_title = await get_status_title(status)

        return await interaction.edit_original_response(
            content=f"**Вы установили редактору {member.mention} `{maker.nickname}` статус `{status_title}`.**"
        )

    @maker.sub_command(name="warn", description="Выдать редактору выговор")
    async def maker_warn(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            reason: str = commands.Param(name="reason", description="Причина")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="warns",
            value=(maker.warns + 1)
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="warn",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы выдали выговор редактору {member.mention} `{maker.nickname}`. Причина: {reason}**"
        )

    @maker.sub_command(name="unwarn", description="Снять редактору выговор")
    async def maker_warn(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            member: disnake.User | disnake.Member = commands.Param(name="maker",
                                                                   description="Редактор или его Discord ID"),
            reason: str = commands.Param(name="reason", description="Причина")
    ):
        await interaction.response.defer()

        interaction_author = methods.get_maker(interaction.author.id)

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        maker = methods.get_maker(member.id)

        if not maker:
            return await interaction.edit_original_response(
                content="**Редактор не зарегистрирован в системе.**"
            )

        elif int(interaction_author.level) <= int(maker.level) and (not int(interaction_author.level) >= 3):
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав чтобы сделать это.**"
            )

        if maker.warns <= 0:
            return await interaction.edit_original_response(
                content="**Вы не можете установить отрицательное кол-во выговоров редактору.**"
            )

        methods.update_maker(
            discord_id=member.id,
            column_name="warns",
            value=(maker.warns - 1)
        )

        methods.add_maker_action(
            maker_id=maker.id,
            made_by=interaction_author.id,
            action="unwarn",
            reason=reason
        )

        return await interaction.edit_original_response(
            content=f"**Вы сняли выговор редактору {member.mention} `{maker.nickname}`. Причина: {reason}**"
        )


def setup(bot: commands.Bot):
    bot.add_cog(Main(bot=bot))
