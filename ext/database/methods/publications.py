from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Publication


async def add_publication(guild_id: int, publication_id: int) -> Publication:
    new_publication = Publication(guild_id=guild_id, publication_number=publication_id)
    async with SessionLocal() as session:
        session.add(new_publication)
        await session.commit()
        publication = await session.execute(
            select(Publication).filter_by(guild_id=guild_id, publication_number=publication_id))
        return publication.scalar()


async def update_publication(
        publication_id: int,
        column_name: Literal[
            "id",
            "guild_id",
            "publication_number",
            "maker_id",
            "date",
            "information_creator_id",
            "status",
            "amount_dp",
            "salary_payer_id",
        ],
        value: int | str | None,
) -> None:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(publication_number=publication_id))
        if publication:
            publication = publication.scalar()
            setattr(publication, column_name, value)
            await session.commit()


async def delete_publication(guild_id: int, publication_id: int) -> None:
    async with SessionLocal() as session:
        publication = await session.execute(
            select(Publication).filter_by(guild_id=guild_id, publication_number=publication_id))
        if publication:
            publication = publication.scalar()
            await session.delete(publication)
            await session.commit()


async def is_publication_exists(guild_id: int, publication_id: int) -> bool:
    async with SessionLocal() as session:
        publication = await session.execute(
            select(Publication).filter_by(guild_id=guild_id, publication_number=publication_id))
        return publication.scalar() is not None


async def get_publication(guild_id: int, publication_id: int) -> Publication | None:
    async with SessionLocal() as session:
        publication = await session.execute(
            select(Publication).filter_by(guild_id=guild_id, publication_number=publication_id))
        return publication.scalar()


async def get_publication_by_id(id: int) -> Publication | None:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(id=id))
        return publication.scalar()


async def get_all_publications(guild_id: int) -> list[Publication] | None:
    async with SessionLocal() as session:
        publications = await session.execute(select(Publication).filter_by(guild_id=guild_id))
        return publications.scalars().all()
