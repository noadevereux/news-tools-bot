import disnake
from utils.databases.access_db import AccessDataBase

access_db = AccessDataBase()

async def command_access_checker(
        guild: disnake.Guild,
        member: disnake.Member,
        command_name: str
) -> bool:
    """
    Checks if member has an access to the command.

    Parameters
    ----------
    guild: :class:`disnake.Guild`
        Guild.
    member: :class:`disnake.Member`
        Member.
    command_name: :class:`str`
        Command name.
    
    Returns
    -------
    :class:`bool`
        True if member has an access, False if it hasn't.
    """
    allowed_roles_ids = await access_db.get_access(command_name)
    if allowed_roles_ids is None:
        return False
    allowed_roles = [guild.get_role(role_id) for role_id in allowed_roles_ids]
    for role in allowed_roles:
        if role in member.roles:
            return True
    return False
