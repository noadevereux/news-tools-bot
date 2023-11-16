import disnake
from disnake.ext import commands
from ext.database.methods import makers as maker_methods, guilds as guild_methods
from ext.models.checks import is_guild_admin
from config import DEV_GUILDS
from ext.models.autocompleters import guild_autocomplete


class DeveloperCommands(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(name="dev", description="[DEV] Команды разработчика", guild_ids=DEV_GUILDS,
                            dm_permission=False)
    @is_guild_admin()
    async def dev(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev.sub_command_group(name="maker", description="[DEV] Управление аккаунтами редакторов")
    async def dev_maker(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @dev_maker.sub_command(name="register", description="[DEV] Зарегистрировать аккаунт редактора")
    async def dev_maker_register(
            self,
            interaction: disnake.ApplicationCommandInteraction,
            guild_id: int = commands.Param(name="guild", description="Выберите сервер",
                                           autocomplete=guild_autocomplete),
            user: disnake.Member | disnake.User = commands.Param(name="user", description="Пользователь"),
            nickname: str = commands.Param(name="nickname", description="Никнейм")
    ):
        await interaction.response.defer()

        guild = await guild_methods.get_guild_by_id(id=guild_id)

        if not guild:
            return await interaction.edit_original_response(
                content=f"**Сервера с ID `{guild_id}` не существует.**"
            )

        maker = await maker_methods.get_maker(guild_id=guild.id, discord_id=user.id)

        if maker:
            return await interaction.edit_original_response(
                content=f"**Редактор {user.mention} уже зарегистрирован в системе и привязан к указанному серверу.**"
            )

        await maker_methods.add_maker(guild_id=guild.id, discord_id=user.id, nickname=nickname)

        return await interaction.edit_original_response(
            content=f"**Вы зарегистрировали редактора {user.mention} `{nickname}` на сервере `{guild.guild_name}`.**"
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(DeveloperCommands(bot=bot))
