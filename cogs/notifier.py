import disnake
from disnake.ext import commands

from config import CHIEF_ROLE_ID, MAKER_ROLE_ID, MAKERS_CHAT_ID


class Notifier(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener(name="on_member_update")
    async def role_given_notify(self, before: disnake.Member, after: disnake.Member):
        maker_role = after.guild.get_role(MAKER_ROLE_ID)
        chief_role = after.guild.get_role(CHIEF_ROLE_ID)
        makers_channel = after.guild.get_channel(MAKERS_CHAT_ID)

        async for entry in after.guild.audit_logs(
            limit=1, action=disnake.AuditLogAction.member_role_update
        ):
            if (maker_role not in entry.before) and (maker_role in entry.after):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была выдана роль {maker_role.mention} ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была выдана роль {maker_role.mention} модератором {entry.user.mention}."
                    )
            elif (maker_role in entry.before) and (maker_role not in entry.after):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была снята роль {maker_role.mention} ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была снята роль {maker_role.mention} модератором {entry.user.mention}."
                    )

            if (chief_role not in entry.before) and (chief_role in entry.after):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была выдана роль {chief_role.mention} ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была выдана роль {chief_role.mention} модератором {entry.user.mention}."
                    )
            elif (chief_role in entry.before) and (chief_role not in entry.after):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была снята роль {chief_role.mention} ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• `WARNING` Пользователю {entry.target.mention} была снята роль {chief_role.mention} модератором {entry.user.mention}."
                    )


def setup(bot: commands.Bot):
    bot.add_cog(Notifier(bot=bot))
