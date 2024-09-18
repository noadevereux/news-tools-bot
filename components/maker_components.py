import asyncio
from datetime import datetime
from typing import Literal

import disnake
from disnake import ui, MessageInteraction, ModalInteraction

from config import DEFAULT_POST_TITLES
from database.methods import (
    makers as maker_methods,
    guilds as guild_methods,
    maker_logs as logs_methods
)
from ext.tools import validate_date, get_status_title
from ext.profile_getters import get_maker_profile
from ext.models.reusable import *


class MakersListPaginator(ui.View):
    def __init__(self, embeds: list[disnake.Embed]):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.current_page = 0

        embed: disnake.Embed
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Страница {i + 1} из {len(embeds)}")

        self._update_state()

    @classmethod
    async def create(cls, guild_id: int):
        makers = await maker_methods.get_all_makers_sorted_by_lvl(guild_id=guild_id)
        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if len(makers) == 0:
            embed = disnake.Embed(
                title=f"🧾 Состав новостного раздела {guild.guild_name}",
                colour=0x2B2D31,
                description="**На сервере нет зарегистрированных редакторов. "
                            "Интересно, как вы смогли использовать команду? Держите промокод на бесплатную пиццу: ||ilovenewstools||.**",
            )

            return None, embed

        next_embed_iteration = 10
        embeds = []
        for i in range(len(makers)):
            match makers[i].account_status:
                case True:
                    emoji_status = "🚹"
                case _:
                    emoji_status = "📛"

            if makers[i].post_name:
                post_name = makers[i].post_name
            else:
                post_name = "не установлена"

            if i == 0:
                new_embed = disnake.Embed(
                    title=f"🧾 Состав новостного раздела {guild.guild_name}",
                    colour=0x2B2D31,
                    description=f"### **Статус | ID | Никнейм | Discord | Должность**\n\n"
                                f"- **{emoji_status} | [ID: {makers[i].id}] | {makers[i].nickname} | <@{makers[i].discord_id}> | {post_name}**\n",
                )
                embeds.append(new_embed)
                continue

            if i == next_embed_iteration:
                new_embed = disnake.Embed(
                    title=f"🧾 Состав новостного раздела {guild.guild_name}",
                    colour=0x2B2D31,
                    description=f"### **Статус | ID | Никнейм | Discord | Должность**\n\n"
                                f"- **{emoji_status} | [ID: {makers[i].id}] | {makers[i].nickname} | <@{makers[i].discord_id}> | {post_name}**\n",
                )
                embeds.append(new_embed)
                next_embed_iteration += 10
                continue

            embeds[-1].description += f"- **{emoji_status} | [ID: {makers[i].id}] | {makers[i].nickname} | <@{makers[i].discord_id}> | {post_name}**\n"  # @formatter:off

        return cls(embeds=embeds), embeds[0]

    def _update_state(self) -> None:
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.embeds) - 1

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.current_page -= 1
        self._update_state()

        await inter.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        self.current_page += 1
        self._update_state()

        await inter.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )


class LogsPaginator(ui.View):
    def __init__(self, embeds: list[disnake.Embed]):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.current_page = 0

        embed: disnake.Embed
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Страница {i + 1} из {len(embeds)}")

        self._update_state()

    @classmethod
    async def create(cls, maker_id: int):
        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if not maker:
            return None, get_failed_embed("Редактор не найден.")

        maker_logs = await logs_methods.get_maker_logs(maker_id=maker.id)

        if len(maker_logs) == 0:
            embed = get_failed_embed("Записи не найдены.")

            return None, embed

        next_embed_iteration = 10
        embeds = []
        for i in range(len(maker_logs)):
            if i == 0:
                new_embed = disnake.Embed(
                    title=f"<:log:1257710061112004669> Логи редактора {maker.nickname}",
                    colour=0x2B2D31,
                    description=f"- **`{maker_logs[i].log}`** ({disnake.utils.format_dt(maker_logs[i].timestamp)})\n",
                )
                embeds.append(new_embed)
                continue

            if i == next_embed_iteration:
                new_embed = disnake.Embed(
                    title=f"<:log:1257710061112004669> Логи редактора {maker.nickname}",
                    colour=0x2B2D31,
                    description=f"- **`{maker_logs[i].log}`** ({disnake.utils.format_dt(maker_logs[i].timestamp)})\n",
                )
                embeds.append(new_embed)
                next_embed_iteration += 10
                continue

            embeds[-1].description += f"- **`{maker_logs[i].log}`** ({disnake.utils.format_dt(maker_logs[i].timestamp)})\n"  # @formatter:off

        return cls(embeds=embeds), embeds[0]

    def _update_state(self) -> None:
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.embeds) - 1

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_page -= 1
        self._update_state()

        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.current_page += 1
        self._update_state()

        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )


class GearButton(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)

        self.author = author
        self.maker_id = maker_id

    @ui.button(emoji="<:service_gear:1207389592815407137>")
    async def open_editor(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        main_menu = await MainMenu.create(author=self.author, maker_id=self.maker_id)

        return await interaction.response.edit_message(view=main_menu)


class MainMenu(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)

        self.author = author
        self.maker_id = maker_id

    @classmethod
    async def create(cls, author: disnake.Member, maker_id: int):
        self = cls(author=author, maker_id=maker_id)
        dropdown_item = await OptionSelect.create(author=author, maker_id=maker_id)
        self.add_item(dropdown_item)
        return self

    @ui.button(label="Отмена", style=disnake.ButtonStyle.red, row=2)
    async def cancel_callback(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        return await interaction.response.edit_message(
            view=GearButton(author=self.author, maker_id=self.maker_id)
        )


class BackToMenu(ui.Button):
    def __init__(self, row: int, author: disnake.Member, maker_id: int):
        super().__init__(style=disnake.ButtonStyle.blurple, label="Назад", row=row)

        self.author = author
        self.maker_id = maker_id

    async def callback(self, interaction: MessageInteraction, /) -> None:
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        main_menu = await MainMenu.create(author=self.author, maker_id=self.maker_id)
        return await interaction.response.edit_message(view=main_menu)


class OptionSelect(ui.StringSelect):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(
            placeholder="🧾 | Выберите опцию из списка",
            row=1,
            options=[
                disnake.SelectOption(
                    label="Управление выговорами",
                    value="warns",
                    emoji="<:warn_sign:1207315803893145610>",
                ),
                disnake.SelectOption(
                    label="Управление предупреждениями",
                    value="preds",
                    emoji="<:pred_sign:1207316150044590081>",
                ),
                disnake.SelectOption(
                    label="Изменить Discord",
                    value="discord",
                    emoji="<:discord_icon:1207328653734584371>",
                ),
                disnake.SelectOption(
                    label="Изменить никнейм",
                    value="nickname",
                    emoji="<:id_card:1207329341227147274>",
                ),
            ],
        )

        self.author = author
        self.maker_id = maker_id

    @classmethod
    async def create(cls, author: disnake.Member, maker_id: int):
        self = cls(author=author, maker_id=maker_id)
        maker = await maker_methods.get_maker_by_id(id=maker_id)

        if maker.account_status:
            self.add_option(
                label="Изменить уровень доступа",
                value="level",
                emoji="<:access_key:1207330321075535882>",
            )
            self.add_option(
                label="Изменить должность",
                value="post_name",
                emoji="<:job_title:1207331119176089681>",
            )
            self.add_option(
                label="Изменить статус",
                value="status",
                emoji="<:status:1207331595497771018>",
            )
            self.add_option(
                label="Изменить дату постановления",
                value="date",
                emoji="<:yellow_calendar:1207339611911884902>",
            )
            self.add_option(
                label="Деактивировать аккаунт",
                value="deactivate",
                emoji="<:deactivate:1207388118370619463>",
            )
        else:
            self.add_option(
                label="Активировать аккаунт",
                value="activate",
                emoji="<:activate:1207344226300596264>",
            )

        self.add_option(
            label="Посмотреть логи действий",
            value="logs",
            emoji="<:log:1257710061112004669>"
        )

        return self

    async def callback(self, interaction: MessageInteraction, /):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        selected_item = self.values[0]

        match selected_item:
            case "warns":
                return await interaction.response.edit_message(
                    view=WarnsControl(author=self.author, maker_id=self.maker_id)
                )

            case "preds":
                return await interaction.response.edit_message(
                    view=PredsControl(author=self.author, maker_id=self.maker_id)
                )

            case "discord":
                submit_text = await SubmitText.create(
                    modal_type="discord", author=self.author, maker_id=self.maker_id
                )

                return await interaction.response.send_modal(modal=submit_text)

            case "nickname":
                submit_text = await SubmitText.create(
                    modal_type="nickname", author=self.author, maker_id=self.maker_id
                )

                return await interaction.response.send_modal(modal=submit_text)

            case "level":
                return await interaction.response.edit_message(
                    view=SetLevel(author=self.author, maker_id=self.maker_id)
                )

            case "post_name":
                submit_text = await SubmitText.create(
                    modal_type="post_name", author=self.author, maker_id=self.maker_id
                )

                return await interaction.response.send_modal(modal=submit_text)

            case "status":
                return await interaction.response.edit_message(
                    view=SetStatus(author=self.author, maker_id=self.maker_id)
                )

            case "date":
                submit_text = await SubmitText.create(
                    modal_type="date", author=self.author, maker_id=self.maker_id
                )

                return await interaction.response.send_modal(modal=submit_text)

            case "deactivate":
                return await interaction.response.send_modal(
                    modal=SubmitReason(
                        action="deactivate", author=self.author, maker_id=self.maker_id
                    )
                )

            case "activate":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Редактор не зарегистрирован в системе. Используйте `/maker register` чтобы зарегистрировать его.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Редактор не зарегистрирован в системе. Используйте `/maker register` чтобы зарегистрировать его.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif maker.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Аккаунт редактора итак активен.")
                    )

                timestamp = datetime.now().isoformat()

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="account_status",
                    value=True,
                )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="appointment_datetime",
                    value=timestamp,
                )

                if not maker.level == "1":
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="level",
                        value="1",
                    )

                if not maker.post_name == DEFAULT_POST_TITLES.get(1):
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="post_name",
                        value=DEFAULT_POST_TITLES.get(1),
                    )

                if not maker.status == "active":
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="status",
                        value="active",
                    )

                if not maker.warns == 0:
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="warns",
                        value=0,
                    )

                if not maker.preds == 0:
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="preds",
                        value=0,
                    )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} активировал аккаунт редактору {maker.nickname}"
                )

                if guild.duty_role_id:
                    member = interaction.guild.get_member(maker.discord_id)
                    duty_role = interaction.guild.get_role(guild.duty_role_id)

                    try:
                        await member.add_roles(duty_role, reason=f"{interaction_author.nickname} активировал аккаунт")
                    except (disnake.HTTPException, disnake.Forbidden, AttributeError) as error:
                        channel = interaction.guild.get_channel(guild.channel_id)

                        try:
                            if isinstance(error, disnake.HTTPException):
                                await channel.send(
                                    content=f"Мне не удалось выдать роль {duty_role.mention} участнику {member.mention}.\n"
                                            f"Произошла внутренняя ошибка при выполнении запроса."
                                )
                            elif isinstance(error, disnake.Forbidden):
                                await channel.send(
                                    content=f"Мне не удалось выдать роль {duty_role.mention} участнику {member.mention}.\n"
                                            f"У меня недостаточно прав для выполнения данного действия."
                                )
                            elif isinstance(error, AttributeError):
                                await channel.send(
                                    components=f"Мне не удалось найти пользователя <@{maker.discord_id}> чтобы выдать ему роль"
                                )
                        except (disnake.HTTPException, disnake.Forbidden):
                            pass

                main_menu = await MainMenu.create(
                    author=self.author, maker_id=self.maker_id
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed, view=main_menu)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы активировали аккаунт редактора **{maker.nickname}**.")
                )

            case "logs":
                await interaction.response.send_message(embed=get_pending_embed(), ephemeral=True)

                view, embed = await LogsPaginator.create(maker_id=self.maker_id)

                return await interaction.edit_original_response(view=view, embed=embed)


class WarnsControl(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)

        self.author = author
        self.maker_id = maker_id
        self.add_item(
            ui.StringSelect(
                disabled=True,
                row=1,
                options=[
                    disnake.SelectOption(
                        label="Управление выговорами",
                        value="warns",
                        emoji="<:warn_sign:1207315803893145610>",
                        default=True,
                    )
                ],
            )
        )
        self.add_item(BackToMenu(row=3, author=author, maker_id=maker_id))

    @ui.button(
        label="Выдать",
        style=disnake.ButtonStyle.red,
        emoji="<:add:1207396410589315072>",
        row=2,
    )
    async def give_warn(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        return await interaction.response.send_modal(
            modal=SubmitReason(
                action="give_warn", author=self.author, maker_id=self.maker_id
            )
        )

    @ui.button(label="Снять", emoji="<:minus:1207397544100110376>", row=2)
    async def take_warn(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        return await interaction.response.send_modal(
            modal=SubmitReason(
                action="take_warn", author=self.author, maker_id=self.maker_id
            )
        )


class PredsControl(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)

        self.author = author
        self.maker_id = maker_id
        self.add_item(
            ui.StringSelect(
                disabled=True,
                row=1,
                options=[
                    disnake.SelectOption(
                        label="Управление предупреждениями",
                        value="preds",
                        emoji="<:pred_sign:1207316150044590081>",
                        default=True,
                    )
                ],
            )
        )
        self.add_item(BackToMenu(row=3, author=author, maker_id=maker_id))

    @ui.button(
        label="Выдать",
        style=disnake.ButtonStyle.red,
        emoji="<:add:1207396410589315072>",
        row=2,
    )
    async def give_warn(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        return await interaction.response.send_modal(
            modal=SubmitReason(
                action="give_pred", author=self.author, maker_id=self.maker_id
            )
        )

    @ui.button(label="Снять", emoji="<:minus:1207397544100110376>", row=2)
    async def take_warn(
        self, button: ui.Button, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        return await interaction.response.send_modal(
            modal=SubmitReason(
                action="take_pred", author=self.author, maker_id=self.maker_id
            )
        )


class SetLevel(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)
        self.author = author
        self.maker_id = maker_id

        self.add_item(
            ui.StringSelect(
                disabled=True,
                row=1,
                options=[
                    disnake.SelectOption(
                        label="Изменить уровень доступа",
                        value="level",
                        emoji="<:access_key:1207330321075535882>",
                        default=True,
                    )
                ],
            )
        )

        self.add_item(BackToMenu(row=3, author=author, maker_id=maker_id))

    @ui.string_select(
        placeholder="🧾 | Выберите уровень доступа",
        row=2,
        options=[
            disnake.SelectOption(label="1 уровень", value="1", emoji="1️⃣"),
            disnake.SelectOption(label="2 уровень", value="2", emoji="2️⃣"),
            disnake.SelectOption(label="3 уровень", value="3", emoji="3️⃣"),
            disnake.SelectOption(label="4 уровень", value="4", emoji="4️⃣"),
            disnake.SelectOption(label="5 уровень", value="5", emoji="5️⃣"),
        ],
    )
    async def choose_level(
        self, string_select: ui.StringSelect, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        await interaction.response.send_message(embed=get_pending_embed())

        level = interaction.values[0]

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif (
            int(interaction_author.level) <= int(level)
            and not interaction_author.is_admin
        ):
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Вы не можете установить редактору {level} уровень доступа.")
            )

        maker = await maker_methods.get_maker_by_id(id=self.maker_id)

        if not maker:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
            )

        elif (
            int(interaction_author.level) <= int(maker.level)
            and not interaction_author.is_admin
        ):
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif not maker.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Невозможно изменить уровень деактивированному редактору.")
            )

        elif maker.level == level:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Уровень **{level}** уже установлен редактору **{maker.nickname}**.")
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="level",
            value=level,
        )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="post_name",
            value=DEFAULT_POST_TITLES.get(int(level)),
        )

        await logs_methods.add_log(
            maker_id=maker.id,
            log=f"{interaction_author.nickname} установил редактору {maker.nickname} {level} уровень"
        )

        embed = await get_maker_profile(
            maker_id=self.maker_id,
            user=interaction.guild.get_member(maker.discord_id),
        )

        await interaction.message.edit(embed=embed)

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы установили редактору **{maker.nickname}** уровень **{level}**.")
        )


class SetStatus(ui.View):
    def __init__(self, author: disnake.Member, maker_id: int):
        super().__init__(timeout=120)
        self.author = author
        self.maker_id = maker_id

        self.add_item(
            ui.StringSelect(
                disabled=True,
                row=1,
                options=[
                    disnake.SelectOption(
                        label="Изменить статус",
                        value="status",
                        emoji="<:status:1207331595497771018>",
                        default=True,
                    )
                ],
            )
        )

        self.add_item(BackToMenu(row=3, author=author, maker_id=maker_id))

    @ui.string_select(
        placeholder="🧾 | Выберите статус",
        row=2,
        options=[
            disnake.SelectOption(
                label="Активен", value="active", emoji="<:activate:1207344226300596264>"
            ),
            disnake.SelectOption(
                label="Неактивен",
                value="inactive",
                emoji="<:deactivate:1207388118370619463>",
            ),
        ],
    )
    async def choose_status(
        self, string_select: ui.StringSelect, interaction: disnake.MessageInteraction
    ):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        await interaction.response.send_message(embed=get_pending_embed())

        status = interaction.values[0]

        guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

        interaction_author = await maker_methods.get_maker(
            guild_id=guild.id, discord_id=interaction.author.id
        )

        if not interaction_author:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif not interaction_author.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif int(interaction_author.level) < 2:
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        maker = await maker_methods.get_maker_by_id(id=self.maker_id)

        if not maker:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
            )

        elif not maker.guild_id == interaction_author.guild_id:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
            )

        elif (
            int(interaction_author.level) <= int(maker.level)
            and not interaction_author.is_admin
        ):
            return await interaction.edit_original_response(
                embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
            )

        elif not maker.account_status:
            return await interaction.edit_original_response(
                embed=get_failed_embed("Невозможно изменить статус деактивированному редактору.")
            )

        elif maker.status == status:
            return await interaction.edit_original_response(
                embed=get_failed_embed(f"Статус **{get_status_title(status)}** уже установлен редактору **{maker.nickname}**.")
            )

        await maker_methods.update_maker(
            guild_id=guild.id,
            discord_id=maker.discord_id,
            column_name="status",
            value=status,
        )

        await logs_methods.add_log(
            maker_id=maker.id,
            log=f"{interaction_author.nickname} установил редактору {maker.nickname} статус на {get_status_title(status)}"
        )

        status_title = get_status_title(status)

        embed = await get_maker_profile(
            maker_id=self.maker_id,
            user=interaction.guild.get_member(maker.discord_id),
        )

        await interaction.message.edit(
            embed=embed, view=SetStatus(author=self.author, maker_id=self.maker_id)
        )

        return await interaction.edit_original_response(
            embed=get_success_embed(f"Вы установили редактору **{maker.nickname}** статус **{status_title}**.")
        )


class SubmitReason(ui.Modal):
    def __init__(
        self,
        action: Literal[
            "give_warn",
            "take_warn",
            "give_pred",
            "take_pred",
            "deactivate",
        ],
        author: disnake.Member,
        maker_id: int,
    ):
        super().__init__(
            title="Укажите причину",
            components=ui.TextInput(
                label="Причина",
                custom_id="reason",
                placeholder="Укажите причину (макс. 70 символов)",
                required=True,
                max_length=70,
            ),
            timeout=300,
        )

        self.action = action
        self.author = author
        self.maker_id = maker_id

    async def callback(self, interaction: ModalInteraction, /):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        reason = interaction.text_values.get("reason")

        match self.action:
            case "give_warn":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="warns",
                    value=(maker.warns + 1),
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} выдал выговор редактору {maker.nickname}. Причина: {reason}"
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы выдали выговор редактору **{maker.nickname}**. Причина: **{reason}**.")
                )
            case "take_warn":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                if maker.warns <= 0:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Невозможно установить отрицательное количество выговоров.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="warns",
                    value=(maker.warns - 1),
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} снял выговор редактору {maker.nickname}. Причина: {reason}"
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы сняли выговор редактору **{maker.nickname}**. Причина: **{reason}**.")
                )
            case "give_pred":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                if maker.preds < 2:
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="preds",
                        value=(maker.preds + 1),
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} выдал предупреждение редактору {maker.nickname}. Причина: {reason}"
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы выдали предупреждение редактору **{maker.nickname}**. Причина: **{reason}**.")
                    )
                else:
                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} выдал предупреждение редактору {maker.nickname}. Причина: {reason}"
                    )

                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="preds",
                        value=0,
                    )

                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="warns",
                        value=(maker.warns + 1),
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"Система выдала выговор редактору {maker.nickname}. Причина: 3/3 предупреждений"
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы выдали предупреждение редактору **{maker.nickname}**. Причина: **{reason}**.\n"
                                                "⚠️ Система выдала выговор редактору. Причина: 3/3 предупреждений.")
                    )
            case "take_pred":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                if maker.preds > 0:
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="preds",
                        value=(maker.preds - 1),
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} снял предупреждение редактору {maker.nickname}. Причина: {reason}"
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы сняли предупреждение редактору **{maker.nickname}**. Причина: **{reason}**.")
                    )

                elif (maker.preds == 0) and (maker.warns > 0):
                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="preds",
                        value=2,
                    )

                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="warns",
                        value=(maker.warns - 1),
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"Система сняла выговор редактору {maker.nickname}. Причина: распад выговора на 3 предупреждения."
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} снял предупреждение редактору {maker.nickname}. Причина: {reason}"
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы сняли предупреждение редактору **{maker.nickname}**. Причина: **{reason}**.\n"
                                                "⚠️ Система сняла выговор редактору. Причина: распад выговора на 3 предупреждения.")
                    )

                else:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Невозможно установить отрицательное количество предупреждений редактору.")
                    )

            case "deactivate":
                await interaction.response.send_message(embed=get_pending_embed())

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not maker.account_status:
                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Аккаунт редактора **{maker.nickname}** уже деактивирован.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="account_status",
                    value=False,
                )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="level",
                    value="0",
                )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="post_name",
                    value=None,
                )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="status",
                    value="inactive",
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} деактивировал аккаунт редактора {maker.nickname}. Причина: {reason}"
                )

                if guild.duty_role_id:
                    member = interaction.guild.get_member(maker.discord_id)
                    duty_role = interaction.guild.get_role(guild.duty_role_id)

                    try:
                        await member.remove_roles(duty_role, reason=f"{interaction_author.nickname} деактивировал аккаунт")
                    except (disnake.HTTPException, disnake.Forbidden, AttributeError) as error:
                        channel = interaction.guild.get_channel(guild.channel_id)

                        try:
                            if isinstance(error, disnake.HTTPException):
                                await channel.send(
                                    content=f"Мне не удалось снять роль {duty_role.mention} участнику {member.mention}.\n"
                                            f"Произошла внутренняя ошибка при выполнении запроса."
                                )
                            elif isinstance(error, disnake.Forbidden):
                                await channel.send(
                                    content=f"Мне не удалось снять роль {duty_role.mention} участнику {member.mention}.**\n"
                                            f"У меня недостаточно прав для выполнения данного действия."
                                )
                            elif isinstance(error, AttributeError):
                                await channel.send(
                                    components=f"Мне не удалось найти пользователя <@{maker.discord_id}> чтобы снять ему роль"
                                )
                        except (disnake.HTTPException, disnake.Forbidden):
                            pass

                main_menu = await MainMenu.create(
                    author=self.author, maker_id=self.maker_id
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed, view=main_menu)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы деактивировали аккаунт редактора **{maker.nickname}**. Причина: **{reason}**.")
                )


class SubmitText(ui.Modal):
    def __init__(
        self,
        modal_title: str,
        modal_type: Literal["discord", "nickname", "post_name", "date"],
        components: ui.TextInput,
        author: disnake.Member,
        maker_id: int,
    ):
        super().__init__(title=modal_title, components=components, timeout=300)
        self.author = author
        self.maker_id = maker_id
        self.modal_type = modal_type

    @classmethod
    async def create(
        cls,
        modal_type: Literal["discord", "nickname", "post_name", "date"],
        author: disnake.Member,
        maker_id: int,
    ):
        match modal_type:
            case "discord":
                self = cls(
                    modal_title="Укажите Discord ID",
                    modal_type=modal_type,
                    author=author,
                    maker_id=maker_id,
                    components=ui.TextInput(
                        label="Discord ID",
                        custom_id="discord_id",
                        placeholder="Укажите Discord ID нового аккаунта",
                        min_length=17,
                        max_length=22,
                    ),
                )
                return self

            case "nickname":
                self = cls(
                    modal_title="Укажите новый никнейм",
                    modal_type=modal_type,
                    author=author,
                    maker_id=maker_id,
                    components=ui.TextInput(
                        label="Никнейм",
                        custom_id="nickname",
                        placeholder="Укажите новый никнейм (макс. 24 символа)",
                        max_length=24,
                    ),
                )
                return self

            case "post_name":
                self = cls(
                    modal_title="Укажите должность",
                    modal_type=modal_type,
                    author=author,
                    maker_id=maker_id,
                    components=ui.TextInput(
                        label="Должность",
                        custom_id="post_name",
                        placeholder="Оставьте пустым для установки по-умолчанию",
                        max_length=32,
                        required=False,
                    ),
                )
                return self

            case "date":
                self = cls(
                    modal_title="Укажите дату постановления",
                    modal_type=modal_type,
                    author=author,
                    maker_id=maker_id,
                    components=ui.TextInput(
                        label="Дата постановления",
                        custom_id="date",
                        placeholder="В формате ГГГГ-ММ-ДД",
                        min_length=10,
                        max_length=10,
                    ),
                )
                return self

    async def callback(self, interaction: ModalInteraction, /):
        if not interaction.author == self.author:
            return await interaction.send(
                embed=get_failed_embed("Вы не можете взаимодействовать с компонентом, который был вызван не вами."),
                ephemeral=True,
            )

        match self.modal_type:
            case "discord":
                await interaction.response.send_message(embed=get_pending_embed())

                new_member = disnake.Object(
                    int(interaction.text_values.get("discord_id"))
                )

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                if maker.discord_id == new_member.id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"К аккаунту редактора **{maker.nickname}** уже привязан Discord ID **{new_member.id}**.")
                    )

                if await maker_methods.is_maker_exists(
                    guild_id=guild.id, discord_id=new_member.id
                ):
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Discord ID **{new_member.id}** уже привязан другому аккаунту.")
                    )
                
                if interaction_author.discord_id == maker.discord_id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )
                    
                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_message(
                        embed=get_failed_embed("Вы не можете изменить Discord ID для своего аккаунта.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="discord_id",
                    value=new_member.id,
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} сменил Discord редактора {maker.nickname} с {maker.discord_id} на {new_member.id}"
                )

                main_menu = await MainMenu.create(
                    author=self.author, maker_id=self.maker_id
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(new_member.id),
                )

                await interaction.message.edit(embed=embed, view=main_menu)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы изменили Discord ID редактору **{maker.nickname}** с **{maker.discord_id}** на **{new_member.id}**.")
                )

            case "nickname":
                await interaction.response.send_message(embed=get_pending_embed())

                nickname = interaction.text_values.get("nickname")

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif maker.nickname == nickname:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Никнейм **{nickname}** уже установлен редактору.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="nickname",
                    value=nickname,
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} сменил редактору никнейм с {maker.nickname} на {nickname}"
                )

                main_menu = await MainMenu.create(
                    author=self.author, maker_id=self.maker_id
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed, view=main_menu)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы изменили никнейм редактора <@{maker.discord_id}> с **{maker.nickname}** на **{nickname}**.")
                )

            case "post_name":
                await interaction.response.send_message(embed=get_pending_embed())

                post = interaction.text_values.get("post_name")

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not maker.account_status:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Невозможно изменить должность деактивированному редактору.")
                    )

                if not post == "":
                    if maker.post_name == post:
                        main_menu = await MainMenu.create(
                            author=self.author, maker_id=self.maker_id
                        )

                        await interaction.message.edit(view=main_menu)

                        return await interaction.edit_original_response(
                            embed=get_failed_embed(f"Должность **{post}** уже установлена редактору **{maker.nickname}**.")
                        )

                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="post_name",
                        value=post,
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} установил редактору {maker.nickname} должность {post}"
                    )

                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed, view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы установили редактору **{maker.nickname}** должность **{post}**.")
                    )

                else:
                    if maker.post_name == DEFAULT_POST_TITLES.get(int(maker.level)):
                        main_menu = await MainMenu.create(
                            author=self.author, maker_id=self.maker_id
                        )

                        await interaction.message.edit(view=main_menu)

                        return await interaction.edit_original_response(
                            embed=get_failed_embed(f"У редактора **{maker.nickname}** уже установлена стандартная должность **{maker.post_name}**.")
                        )

                    await maker_methods.update_maker(
                        guild_id=guild.id,
                        discord_id=maker.discord_id,
                        column_name="post_name",
                        value=DEFAULT_POST_TITLES.get(int(maker.level)),
                    )

                    await logs_methods.add_log(
                        maker_id=maker.id,
                        log=f"{interaction_author.nickname} установил редактору {maker.nickname} должность {DEFAULT_POST_TITLES.get(int(maker.level))}"
                    )

                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    embed = await get_maker_profile(
                        maker_id=self.maker_id,
                        user=interaction.guild.get_member(maker.discord_id),
                    )

                    await interaction.message.edit(embed=embed, view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_success_embed(f"Вы установили редактору **{maker.nickname}** стандартную должность **{DEFAULT_POST_TITLES.get(int(maker.level))}**.")
                    )

            case "date":
                await interaction.response.send_message(embed=get_pending_embed())

                date_str = interaction.text_values.get("date")

                is_date_valid = validate_date(date_str)

                if not is_date_valid:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Неверный формат даты. Укажите дату в формате `ГГГГ-ММ-ДД`.")
                    )

                new_datetime = datetime.fromisoformat(date_str)

                if new_datetime > datetime.now():
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("Дату постановления нельзя указать в будещем.")
                    )

                guild = await guild_methods.get_guild(discord_id=interaction.guild.id)

                interaction_author = await maker_methods.get_maker(
                    guild_id=guild.id, discord_id=interaction.author.id
                )

                if not interaction_author:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif not interaction_author.account_status:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                elif int(interaction_author.level) < 2:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                maker = await maker_methods.get_maker_by_id(id=self.maker_id)

                if not maker:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif not maker.guild_id == interaction_author.guild_id:
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed(f"Редактор c ID **{self.maker_id}** не зарегистрирован в системе.")
                    )

                elif (
                    int(interaction_author.level) <= int(maker.level)
                    and not interaction_author.is_admin
                ):
                    main_menu = await MainMenu.create(
                        author=self.author, maker_id=self.maker_id
                    )

                    await interaction.message.edit(view=main_menu)

                    return await interaction.edit_original_response(
                        embed=get_failed_embed("У вас недостаточно прав для выполнения данного взаимодействия.")
                    )

                await maker_methods.update_maker(
                    guild_id=guild.id,
                    discord_id=maker.discord_id,
                    column_name="appointment_datetime",
                    value=new_datetime,
                )

                await logs_methods.add_log(
                    maker_id=maker.id,
                    log=f"{interaction_author.nickname} установил редактору {maker.nickname} дату постановления на {date_str}"
                )

                main_menu = await MainMenu.create(
                    author=self.author, maker_id=self.maker_id
                )

                embed = await get_maker_profile(
                    maker_id=self.maker_id,
                    user=interaction.guild.get_member(maker.discord_id),
                )

                await interaction.message.edit(embed=embed, view=main_menu)

                return await interaction.edit_original_response(
                    embed=get_success_embed(f"Вы установили дату постановления редактора **{maker.nickname}** на <t:{int(new_datetime.timestamp())}:D>.")
                )
