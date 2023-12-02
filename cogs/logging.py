from datetime import datetime

import disnake
from disnake.ext import commands

from ext.database.methods import guilds as guild_methods
from ext.models.keyboards import ConfirmRoleAction


class Notifier(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener(name=disnake.Event.audit_log_entry_create)
    async def role_notify(self, entry: disnake.AuditLogEntry):
        if not entry.action == disnake.AuditLogAction.member_role_update:
            return

        guild = await guild_methods.get_guild(discord_id=entry.guild.id)

        if not guild:
            return
        if not guild.is_notifies_enabled:
            return

        roles: list[disnake.Role] = [entry.guild.get_role(role_id) for role_id in guild.roles_list]
        channel = entry.guild.get_channel_or_thread(guild.channel_id)

        if len(roles) == 0:
            return
        if not channel:
            return

        for role in roles:
            if (role in entry.before.roles) and (role not in entry.after.roles):
                message = await channel.send(
                    content=f"**`[WARNING]` -> Модератор <@{entry.user.id}> снял роль <@&{role.id}> участнику <@{entry.target.id}>.**",
                    view=ConfirmRoleAction(),
                    allowed_mentions=disnake.AllowedMentions(users=[entry.user], roles=False)
                )
                try:
                    await message.pin(reason="Действие требует подтверждения")
                except (disnake.errors.Forbidden, disnake.errors.NotFound, disnake.errors.HTTPException):
                    pass
                async for msg in channel.history(limit=5):
                    if msg.type == disnake.MessageType.pins_add:
                        try:
                            await msg.delete()
                        except (disnake.errors.Forbidden, disnake.errors.NotFound, disnake.errors.HTTPException):
                            pass
            elif (role not in entry.before.roles) and (role in entry.after.roles):
                message = await channel.send(
                    content=f"**`[WARNING]` -> Модератор <@{entry.user.id}> выдал роль <@&{role.id}> участнику <@{entry.target.id}>.**",
                    view=ConfirmRoleAction(),
                    allowed_mentions=disnake.AllowedMentions(users=[entry.user], roles=False)
                )
                try:
                    await message.pin(reason="Действие требует подтверждения")
                except (disnake.errors.Forbidden, disnake.errors.NotFound, disnake.errors.HTTPException):
                    pass
                async for msg in channel.history(limit=5):
                    if msg.type == disnake.MessageType.pins_add:
                        try:
                            await msg.delete()
                        except (disnake.errors.Forbidden, disnake.errors.NotFound, disnake.errors.HTTPException):
                            pass

    @commands.Cog.listener(name=disnake.Event.audit_log_entry_create)
    async def log_role_notify(self, entry: disnake.AuditLogEntry):
        if not entry.action == disnake.AuditLogAction.member_role_update:
            return

        guild = await guild_methods.get_guild(discord_id=entry.guild.id)

        if not guild:
            return

        roles: list[disnake.Role] = [entry.guild.get_role(role_id) for role_id in guild.log_roles_list]
        channel = entry.guild.get_channel_or_thread(guild.log_roles_channel)

        if len(roles) == 0:
            return
        if not channel:
            return

        for role in roles:
            if (role in entry.before.roles) and (role not in entry.after.roles):
                embed = disnake.Embed(
                    title="Информация о снятии роли",
                    colour=role.colour,
                    timestamp=datetime.now()
                )
                embed.add_field(name="Роль", value=f"<@&{role.id}>", inline=False)
                embed.add_field(
                    name="Кому сняли роль",
                    value=f"<@{entry.target.id}> `{entry.target.display_name}`",
                    inline=False
                )
                embed.add_field(
                    name="Кто снял роль",
                    value=f"<@{entry.user.id}> `{entry.user.display_name}`",
                    inline=False
                )
                embed.set_footer(text="Роль была снята:")
                await channel.send(embed=embed)
            elif (role not in entry.before.roles) and (role in entry.after.roles):
                embed = disnake.Embed(
                    title="Информация о выдаче роли",
                    colour=role.colour,
                    timestamp=datetime.now()
                )
                embed.add_field(name="Роль", value=f"<@&{role.id}>", inline=False)
                embed.add_field(
                    name="Кому выдали роль",
                    value=f"<@{entry.target.id}> `{entry.target.display_name}`",
                    inline=False
                )
                embed.add_field(
                    name="Кто выдал роль",
                    value=f"<@{entry.user.id}> `{entry.user.display_name}`",
                    inline=False
                )
                embed.set_footer(text="Роль была выдана:")
                await channel.send(embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Notifier(bot=bot))
