from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Guild


async def add_guild(discord_id: int, guild_name: str) -> None:
    guild = Guild(discord_id=discord_id, guild_name=guild_name)
    async with SessionLocal() as session:
        session.add(guild)
        await session.commit()


async def is_guild_exists(discord_id: int) -> bool:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild).filter_by(discord_id=discord_id))
        result = guild.scalar()
    return result is not None


async def get_guild(discord_id: int) -> Guild | None:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild).filter_by(discord_id=discord_id))
        result = guild.scalar()
    return result


async def get_guild_by_id(id: int) -> Guild | None:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild).filter_by(id=id))
        result = guild.scalar()
    return result


async def get_all_guilds() -> list[Guild]:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild))
        result = guild.scalars().all()
    return result


async def update_guild(
        discord_id: int,
        column_name: Literal[
            "id",
            "discord_id",
            "guild_name",
            "roles_list",
            "is_notifies_enabled",
            "channel_id",
            "log_roles_list",
            "log_roles_channel",
            "is_admin_guild",
            "is_active"
        ],
        value
) -> None:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild).filter_by(discord_id=discord_id))
        if guild:
            guild = guild.scalar()
            setattr(guild, column_name, value)
            await session.commit()


async def update_guild_by_id(
        id: int,
        column_name: Literal[
            "id",
            "discord_id",
            "guild_name",
            "roles_list",
            "is_notifies_enabled",
            "channel_id",
            "log_roles_list",
            "log_roles_channel",
            "is_admin_guild",
            "is_active"
        ],
        value
) -> None:
    async with SessionLocal() as session:
        guild = await session.execute(select(Guild).filter_by(id=id))
        if guild:
            guild = guild.scalar()
            setattr(guild, column_name, value)
            await session.commit()
