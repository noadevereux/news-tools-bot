from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..orm_models import Maker, Publication


async def is_maker_exists(discord_id: int) -> bool:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(discord_id=discord_id))
    return maker.scalar() is not None


async def is_maker_exists_by_id(id: int) -> bool:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(id=id))
        return maker.scalar() is not None


async def add_maker(discord_id: int, nickname: str) -> None:
    new_maker = Maker(discord_id=discord_id, nickname=nickname)
    async with SessionLocal() as session:
        session.add(new_maker)
        await session.commit()


async def deactivate_maker(discord_id: int) -> None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(discord_id=discord_id))
        if maker:
            maker = maker.scalar()
            maker.account_status = False
            await session.commit()


async def update_maker(
        discord_id: int,
        column_name: Literal[
            "id",
            "discord_id",
            "nickname",
            "level",
            "status",
            "warns",
            "appointment_datetime",
            "account_status",
        ],
        value: str | int,
) -> None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(discord_id=discord_id))
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()


async def update_maker_by_id(
        id: int,
        column_name: Literal[
            "id",
            "discord_id",
            "nickname",
            "level",
            "status",
            "warns",
            "appointment_datetime",
            "account_status",
        ],
        value: str | int,
) -> None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(id=id))
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()


async def get_all_makers() -> list[Maker] | None:
    async with SessionLocal() as session:
        makers = await session.execute(select(Maker))
        return makers.scalars().all()


async def get_maker(discord_id: int) -> Maker | None:
    async with SessionLocal() as session:
        maker = await session.execute(select(Maker).filter_by(discord_id=discord_id))
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
