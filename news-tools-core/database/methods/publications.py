from typing import Literal

from sqlalchemy import select

from ..database import SessionManager
from ..models import Publication


async def add_publication(guild_id: int, publication_number: int) -> Publication:
    new_publication = Publication(
        guild_id=guild_id, publication_number=publication_number
    )
    async with SessionManager() as session:
        session.add(new_publication)
        await session.commit()
        publication = await session.execute(
            select(Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        return publication.scalar()


async def update_publication(
        guild_id: int,
        publication_number: int,
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
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        if publication:
            publication = publication.scalar()
            setattr(publication, column_name, value)
            await session.commit()


async def update_publication_by_id(
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
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(id=publication_id)
        )
        if publication:
            publication = publication.scalar()
            setattr(publication, column_name, value)
            await session.commit()


async def delete_publication(guild_id: int, publication_number: int) -> None:
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        if publication:
            publication = publication.scalar()
            await session.delete(publication)
            await session.commit()


async def delete_publication_by_id(publication_id: int) -> None:
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(id=publication_id)
        )
        if publication:
            publication = publication.scalar()
            await session.delete(publication)
            await session.commit()


async def is_publication_exists(guild_id: int, publication_id: int) -> bool:
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(
                guild_id=guild_id, publication_number=publication_id
            )
        )
        return publication.scalar() is not None


async def get_publication(guild_id: int, publication_number: int) -> Publication | None:
    async with SessionManager() as session:
        publication = await session.execute(
            select(Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        return publication.scalar()


async def get_publication_by_id(id: int) -> Publication | None:
    async with SessionManager() as session:
        publication = await session.execute(select(Publication).filter_by(id=id))
        return publication.scalar()


async def get_all_publications(guild_id: int = None) -> list[Publication] | None:
    async with SessionManager() as session:
        if guild_id:
            publications = await session.execute(
                select(Publication).filter_by(guild_id=guild_id)
            )
        else:
            publications = await session.execute(select(Publication))
        return publications.scalars().all()
