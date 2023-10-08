import disnake
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

    @commands.slash_command(name="apitoken", description="[DEV] Получить токен для API")
    @commands.is_owner()
    async def api_token(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            username: str = commands.Param(name="username", description="Имя пользователя токена")
    ):
        await interaction.response.defer(ephemeral=True)

        token = sign_jwt(username)

        return await interaction.edit_original_response(
            content=f"**JWT для пользователя {username}**\n**||```{token}```||**\n*Храните токен в безопасном месте, никому его не передавайте.*\n*Токен подлежит замене через 30 дней.*"
        )

    @tasks.loop(count=1)
    async def start_server(self) -> None:
        await start_server(self.bot)


def setup(bot: commands.Bot):
    bot.add_cog(API(bot))
