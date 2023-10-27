import datetime

import disnake
from disnake.ext import commands

from ext.database.methods import guilds as guild_methods, makers as maker_methods, publications as publication_methods, \
    publication_actions as action_methods
from ext.logger import Logger
from ext.tools import validate_date, get_publication_profile, get_status_title

from ext.models.checks import is_guild_exists


class Publications(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.log = Logger("cogs.publications.py.log")

    @commands.slash_command(name="pubsetting", description="Настройка выпусков", dm_permission=False)
    @is_guild_exists()
    async def pubsetting(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @pubsetting.sub_command(name="create", description="Создать выпуск")
    async def pubsetting_create(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` уже существует.**"
            )

        new_publication = await publication_methods.add_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        await action_methods.add_pub_action(
            pub_id=new_publication.id,
            made_by=interaction_author.id,
            action="createpub"
        )

        embed = await get_publication_profile(
            guild_id=guild.id,
            publication_id=new_publication.publication_number
        )

        return await interaction.edit_original_response(
            content=f"**Вы создали выпуск `#{new_publication.publication_number}`.**",
            embed=embed
        )

    @pubsetting.sub_command(name="delete", description="[DANGER] Удалить выпуск")
    async def pubsetting_delete(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif int(interaction_author.level) < 3:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` итак не существует.**"
            )

        await publication_methods.delete_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        await action_methods.add_pub_action(
            pub_id=publication.id,
            made_by=interaction_author.id,
            action="deletepub",
            meta=publication.id
        )

        return await interaction.edit_original_response(
            content=f"**Вы удалили выпуск с номером `#{publication.publication_number}` `[UID: {publication.id}]`.**"
        )

    @commands.slash_command(name="publication", description="Действия с выпусками", dm_permission=False)
    @is_guild_exists()
    async def publication(
            self,
            interaction: disnake.ApplicationCommandInteraction
    ):
        pass

    @publication.sub_command(name="info", description="Посмотреть информацию о выпуске")
    async def publication_info(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                content="**У вас недостаточно прав для выполнения данной команды.**"
            )

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        embed = await get_publication_profile(
            guild_id=guild.id,
            publication_id=pub_number
        )

        return await interaction.edit_original_response(
            embed=embed
        )

    @pubsetting.sub_command(name="number", description="Изменить номер выпуска")
    async def pubsetting_setnumber(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            old_number: int = commands.Param(name="number", description="Текущий номер выпуска"),
            new_number: int = commands.Param(name="new_number", description="Новый номер выпуска")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        elif old_number == new_number:
            return await interaction.edit_original_response(
                content="**Изменений не произошло, номера старого и нового выпусков совпадают.**"
            )

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=old_number
        )
        new_publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=new_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{old_number}` не существует.**"
            )

        elif new_publication:
            embed = await get_publication_profile(
                guild_id=guild.id,
                publication_id=new_number
            )
            return await interaction.edit_original_response(
                content=f"**Номер выпуска `#{new_number}` уже занят. Информация о выпуске:**",
                embed=embed
            )

        await publication_methods.update_publication(
            guild_id=guild.id,
            publication_id=publication.publication_number,
            column_name="publication_number",
            value=new_number
        )

        await action_methods.add_pub_action(
            pub_id=publication.id,
            made_by=interaction_author.id,
            action="setpub_id",
            meta=f"[{old_number}, {new_number}]"
        )

        return await interaction.edit_original_response(
            content=f"**Вы изменили номер выпуска с уникальным `ID: {publication.id}` с `#{old_number}` на `#{new_number}`.**"
        )

    @pubsetting.sub_command(name="date", description="Изменить дату публикации выпуска")
    async def pubsetting_date(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            date: str = commands.Param(default=None, name="date", description="Дата в формате ГГГГ-ММ-ДД")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        if date:
            is_date_valid = await validate_date(date)

            if not is_date_valid:
                return await interaction.edit_original_response(
                    content="**Неверно указана дата. Укажите дату в формате `ГГГГ-ММ-ДД`, например `2023-01-15`.**"
                )

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        if date:
            if publication.date == datetime.date.fromisoformat(date):
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, дата выпуска такая же, какую вы указали.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="date",
                value=date
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_date",
                meta=date
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили дату выпуска `#{pub_number}` на `{date}`.**"
            )
        elif not date:
            if not publication.date:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, дата выпуска итак не указана.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="date",
                value=None
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_date",
                meta="не указана"
            )

            return await interaction.edit_original_response(
                content=f"**Вы очистили дату выпуска `#{pub_number}`.**"
            )

    @pubsetting.sub_command(name="maker", description="Изменить редактора выпуска")
    async def pubsetting_maker(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            member: disnake.User | disnake.Member = commands.Param(default=None, name="maker",
                                                                   description="Редактор или его Discord ID")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        if member:
            maker = await maker_methods.get_maker(
                guild_id=guild.id,
                discord_id=member.id
            )

            if not maker:
                return await interaction.edit_original_response(
                    content=f"**Пользователь, которого вы указали не зарегистрирован в системе.**"
                )
            elif not maker.account_status:
                return await interaction.edit_original_response(
                    content=f"**Аккаунт редактора, которого вы указали, деактивирован.**"
                )

            if publication.maker_id == maker.id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, редактор выпуска установлен такой-же, какого вы указали.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="maker_id",
                value=maker.id
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_maker",
                meta=maker.id
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили редактора выпуска `#{pub_number}` на {member.mention} `{maker.nickname}`.**"
            )
        elif not member:
            if not publication.maker_id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, редактор выпуска итак не указан.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="maker_id",
                value=None
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_maker",
                meta="не указан"
            )

            return await interaction.edit_original_response(
                content=f"**Вы очистили редактора выпуска `#{pub_number}`.**"
            )

    @pubsetting.sub_command(name="status", description="Изменить статус выпуска")
    async def pubsetting_status(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            status: str = commands.Param(name="status", description="Статус выпуска", choices=[
                disnake.OptionChoice(name="Сделан", value="completed"),
                disnake.OptionChoice(name="Провален", value="failed"),
                disnake.OptionChoice(name="В процессе", value="in_process")
            ])
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        elif publication.status == status:
            return await interaction.edit_original_response(
                content=f"**Изменений не произошло, у выпуска `#{pub_number}` уже указан статус, который вы указали.**"
            )

        await publication_methods.update_publication(
            guild_id=guild.id,
            publication_id=pub_number,
            column_name="status",
            value=status
        )

        await action_methods.add_pub_action(
            pub_id=publication.id,
            made_by=interaction_author.id,
            action="setpub_status",
            meta=status
        )

        status_title = await get_status_title(status)

        return await interaction.edit_original_response(
            content=f"**Вы установили выпуску `#{pub_number}` статус `{status_title}`**"
        )

    @pubsetting.sub_command(name="salary", description="Изменить зарплату за выпуск")
    async def pubsetting_salary(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            amount: int = commands.Param(default=None, name="salary", description="Сумма зарплаты за выпуск")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        if amount:
            if publication.amount_dp == amount:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, зарплата за выпуск установлена такая же, какую вы указали.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="amount_dp",
                value=amount
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_amount",
                meta=amount
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили зарплату за выпуск `#{pub_number}` на `{amount}`.**"
            )
        elif not amount:
            if not publication.amount_dp:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, зарплата за выпуск итак не указана.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="amount_dp",
                value=None
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_amount",
                meta="не установлено"
            )

            return await interaction.edit_original_response(
                content=f"**Вы очистили зарплату за выпуск `#{pub_number}`.**"
            )

    @pubsetting.sub_command(name="information_creator", description="Изменить автора информации к выпуску")
    async def pubsetting_information_creator(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            member: disnake.User | disnake.Member = commands.Param(default=None, name="creator",
                                                                   description="Автор информации")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        if member:
            creator = await maker_methods.get_maker(
                guild_id=guild.id,
                discord_id=member.id
            )

            if not creator:
                return await interaction.edit_original_response(
                    content=f"**Пользователь, которого вы указали не зарегистрирован в системе.**"
                )
            elif not creator.account_status:
                return await interaction.edit_original_response(
                    content=f"**Аккаунт редактора, которого вы указали, деактивирован.**"
                )

            if publication.information_creator_id == creator.id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, автор информации выпуска установлен таким же, какого вы указали.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="information_creator_id",
                value=creator.id
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_infocreator",
                meta=creator.id
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили автора информации к выпуску `#{pub_number}` на {member.mention} `{creator.nickname}`.**"
            )
        elif not member:
            if not publication.information_creator_id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, автор информации к выпуску итак не указан.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="information_creator_id",
                value=None
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_infocreator",
                meta="не указан"
            )

            return await interaction.edit_original_response(
                content=f"**Вы очистили автора информации к выпуску `#{pub_number}`.**"
            )

    @pubsetting.sub_command(name="salary_payer", description="Изменить человека, который выплатил зарплату")
    async def pubsetting_salary_payer(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            pub_number: int = commands.Param(name="number", description="Номер выпуска"),
            member: disnake.User | disnake.Member = commands.Param(default=None, name="salary_payer",
                                                                   description="Человек, который выплатил зарплату за выпуск")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id,
            discord_id=interaction.author.id
        )

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

        publication = await publication_methods.get_publication(
            guild_id=guild.id,
            publication_id=pub_number
        )

        if not publication:
            return await interaction.edit_original_response(
                content=f"**Выпуск с номером `#{pub_number}` не существует.**"
            )

        if member:
            salary_payer = await maker_methods.get_maker(
                guild_id=guild.id,
                discord_id=member.id
            )

            if publication.salary_payer_id == salary_payer.id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, человек, который выплати зарплату установлен таким же, какого вы указали.**"
                )

            if not salary_payer:
                return await interaction.edit_original_response(
                    content=f"**Пользователь, которого вы указали не зарегистрирован в системе.**"
                )
            elif not salary_payer.account_status:
                return await interaction.edit_original_response(
                    content=f"**Аккаунт редактора, которого вы указали, деактивирован.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="salary_payer_id",
                value=salary_payer.id
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_salarypayer",
                meta=salary_payer.id
            )

            return await interaction.edit_original_response(
                content=f"**Вы изменили человека, который выплатил зарплату за выпуск `#{pub_number}` на {member.mention} `{salary_payer.nickname}`.**"
            )
        elif not member:
            if not publication.salary_payer_id:
                return await interaction.edit_original_response(
                    content=f"**Изменений не произошло, автор информации к выпуску итак не указан.**"
                )

            await publication_methods.update_publication(
                guild_id=guild.id,
                publication_id=pub_number,
                column_name="salary_payer_id",
                value=None
            )

            await action_methods.add_pub_action(
                pub_id=publication.id,
                made_by=interaction_author.id,
                action="setpub_salarypayer",
                meta="не указан"
            )

            return await interaction.edit_original_response(
                content=f"**Вы очистили человека, который выплатил зарплату за выпуск `#{pub_number}`.**"
            )


def setup(bot: commands.Bot):
    bot.add_cog(cog=Publications(bot=bot))
