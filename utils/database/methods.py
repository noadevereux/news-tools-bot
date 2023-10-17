from typing import Literal
from .orm_models import Maker, MakerAction, Publication, PublicationAction
from .database import SessionLocal
from sqlalchemy import select, desc


# BEGIN MAKERS METHODS

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


# END MAKERS METHODS

# BEGIN PUBLICATIONS METHODS

async def add_publication(publication_id: int) -> Publication:
    new_publication = Publication(publication_number=publication_id)
    async with SessionLocal() as session:
        session.add(new_publication)
        await session.commit()
        publication = await session.execute(select(Publication).filter_by(publication_number=publication_id))
        return publication.scalar()


async def update_publication(
        publication_id: int,
        column_name: Literal[
            "id",
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


async def delete_publication(publication_id: int) -> None:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(publication_number=publication_id))
        if publication:
            publication = publication.scalar()
            session.delete(publication)
            await session.commit()


async def is_publication_exists(publication_id: int) -> bool:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(publication_number=publication_id))
        return publication.scalar() is not None


async def get_publication(publication_id: int) -> Publication | None:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(publication_number=publication_id))
        return publication.scalar()


async def get_publication_by_id(id: int) -> Publication | None:
    async with SessionLocal() as session:
        publication = await session.execute(select(Publication).filter_by(id=id))
        return publication.scalar()


async def get_all_publications() -> list[Publication] | None:
    async with SessionLocal() as session:
        publications = await session.execute(select(Publication))
        return publications.scalars().all()


# END PUBLICATION METHODS

# BEGIN MAKER ACTIONS METHODS

async def add_maker_action(
        maker_id: int,
        made_by: int,
        action: Literal[
            "addmaker",
            "deactivate",
            "setnickname",
            "setdiscord",
            "setlevel",
            "setstatus",
            "warn",
            "unwarn",
        ],
        meta: str = None,
        reason: str = None,
) -> None:
    new_action = MakerAction(
        maker_id=maker_id, made_by=made_by, action=action, meta=meta, reason=reason
    )

    async with SessionLocal() as session:
        session.add(new_action)
        await session.commit()


async def get_makers_actions(maker_id: int) -> list[MakerAction]:
    async with SessionLocal() as session:
        actions = await session.execute(
            select(MakerAction).filter_by(maker_id=maker_id).order_by(MakerAction.timestamp.desc())
        )
        return actions.scalars().all()


async def get_all_maker_actions() -> list[MakerAction]:
    async with SessionLocal() as session:
        actions = await session.execute(select(MakerAction).order_by(MakerAction.timestamp.desc()))
        return actions.scalars().all()


# END MAKER ACTIONS METHODS

# BEGIN PUBLICATION ACTIONS METHODS

async def add_pub_action(
        pub_id: int,
        made_by: int,
        action: Literal[
            "createpub",
            "deletepub",
            "setpub_id",
            "setpub_date",
            "setpub_maker",
            "setpub_status",
            "setpub_amount",
            "setpub_infocreator",
            "setpub_salarypayer",
        ],
        meta: str | int = None,
        reason: str = None,
) -> None:
    new_action = PublicationAction(
        publication_id=pub_id, made_by=made_by, action=action, meta=meta, reason=reason
    )

    async with SessionLocal() as session:
        session.add(new_action)
        await session.commit()


async def get_pubs_actions(pub_id: int) -> list[PublicationAction]:
    async with SessionLocal() as session:
        actions = await session.execute(
            select(PublicationAction).filter_by(publication_id=pub_id).order_by(PublicationAction.timestamp.desc())
        )
        return actions.scalars().all()


async def get_all_pub_actions() -> list[PublicationAction]:
    async with SessionLocal() as session:
        actions = await session.execute(select(PublicationAction).order_by(PublicationAction.timestamp.desc()))
        return actions.scalars().all()

# END PUBLICATION ACTIONS METHODS
