from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import MakerAction


async def add_maker_action(
        maker_id: int,
        made_by: int,
        action: Literal[
            "addmaker",
            "deactivate",
            "setnickname",
            "setdiscord",
            "setlevel",
            "setpost",
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
