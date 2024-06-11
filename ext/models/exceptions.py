from disnake.ext.commands import CommandError

__all__ = ["GuildNotExists", "CommandCalledInDM", "GuildNotAdmin", "UserNotExists", "UserNotAdmin"]


class GuildNotExists(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class CommandCalledInDM(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class GuildNotAdmin(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class UserNotExists(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)


class UserNotAdmin(CommandError):
    def __init__(self, message: str | None = None, *args):
        super().__init__(message=message, *args)
