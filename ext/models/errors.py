from disnake.ext.commands import CommandError


class GuildNotExists(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class CommandCalledInDM(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class GuildNotAdmin(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)
