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
            if (not maker_role in before.roles) and (maker_role in after.roles):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была выдана роль `{maker_role}` ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была выдана роль `{maker_role}` модератором {entry.user.mention}."
                    )
            elif (maker_role in before.roles) and (not maker_role in after.roles):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была снята роль `{maker_role}` ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была снята роль `{maker_role}` модератором {entry.user.mention}."
                    )

            if (not chief_role in before.roles) and (chief_role in after.roles):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была выдана роль `{chief_role}` ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была выдана роль `{chief_role}` модератором {entry.user.mention}."
                    )
            elif (chief_role in before.roles) and (not chief_role in after.roles):
                if entry.user.bot:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была снята роль `{chief_role}` ботом {entry.user.mention}."
                    )
                else:
                    await makers_channel.send(
                        content=f"• {chief_role.mention} `WARNING` Пользователю {entry.target.mention} была снята роль `{chief_role}` модератором {entry.user.mention}."
                    )


def setup(bot: commands.Bot):
    bot.add_cog(Notifier(bot=bot))
