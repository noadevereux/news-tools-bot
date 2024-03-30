from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Maker, Publication


async def is_maker_exists(guild_id: int, discord_id: int) -> bool:
    async with SessionLocal() as session:
        maker = await session.execute(
            select(Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
    return maker.scalar() is not None


async def is_maker_exists_by_id(id: int) -> bool:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(id=id))
        return maker.scalar() is not None


async def add_maker(guild_id: int, discord_id: int, nickname: str) -> Maker | None:
    new_maker = Maker(guild_id=guild_id, discord_id=discord_id, nickname=nickname)
    async with SessionLocal() as session:
        session.add(new_maker)
        await session.commit()
        maker = await session.execute(
            select(Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
    return maker.scalar()


async def update_maker(
    guild_id: int,
    discord_id: int,
    column_name: Literal[
        "id",
        "guild_id",
        "discord_id",
        "nickname",
        "level",
        "post_name",
        "status",
        "warns",
        "preds",
        "appointment_datetime",
        "account_status",
    ],
    value,
) -> None:
    async with SessionLocal() as session:
        maker = await session.execute(
            select(Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()


async def update_maker_by_id(
    id: int,
    column_name: Literal[
        "id",
        "guild_id",
        "discord_id",
        "nickname",
        "level",
        "post_name",
        "status",
        "warns",
        "preds",
        "appointment_datetime",
        "account_status",
    ],
    value,
) -> None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(id=id))
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()


async def get_all_makers(guild_id: int) -> list[Maker] | None:
    async with SessionLocal() as session:
        makers = await session.execute(select(Maker).filter_by(guild_id=guild_id))
        return makers.scalars().all()


async def get_all_makers_sorted_by_lvl(guild_id: int) -> list[Maker] | None:
    async with SessionLocal() as session:
        makers = await session.execute(
            select(Maker).filter_by(guild_id=guild_id).order_by(Maker.level.desc())
        )
        return makers.scalars().all()


async def get_maker(guild_id: int, discord_id: int) -> Maker | None:
    async with SessionLocal() as session:
        maker = await session.execute(
            select(Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
        return maker.scalar()


async def get_maker_by_id(id: int) -> Maker | None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(id=id))
        return maker.scalar()


async def get_publications_by_maker(id: int) -> list[Publication]:
    async with SessionLocal() as session:
        publications = await session.execute(
            select(Publication).filter_by(maker_id=id, status="completed")
        )
        return publications.scalars().all()
