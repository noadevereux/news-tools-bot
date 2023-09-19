from disnake.ext import commands, tasks

from api.main import start_server
from api.auth.auth_handler import sign_jwt


class API(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        self.start_server.start()

    @commands.command(name="apitoken")
    @commands.is_owner()
    async def api_token(self, ctx: commands.Context, username: str):
        async with ctx.typing():
            token = sign_jwt(username=username)
        await ctx.message.add_reaction("✅")
        return await ctx.message.reply(
            content=f"**JWT для пользователя {username}: ||`{token}`||.**\n\n*Храните токен в безопасном месте, никому его не передавайте.*\n*Токен подлежит замене через 30 дней.*"
        )

    @tasks.loop(count=1)
    async def start_server(self) -> None:
        await start_server(self.bot)


def setup(bot: commands.Bot):
    bot.add_cog(API(bot))
