from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import PublicationAction


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
            select(PublicationAction)
            .filter_by(publication_id=pub_id)
            .order_by(PublicationAction.timestamp.desc())
        )
        return actions.scalars().all()


async def get_all_pub_actions() -> list[PublicationAction]:
    async with SessionLocal() as session:
        actions = await session.execute(
            select(PublicationAction).order_by(PublicationAction.timestamp.desc())
        )
        return actions.scalars().all()
