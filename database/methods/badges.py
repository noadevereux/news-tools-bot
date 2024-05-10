from typing import Literal

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Badge, AwardedBadge


async def add_badge(name: str, emoji: str):
    new_badge = Badge(name=name, emoji=emoji)
    async with SessionLocal() as session:
        session.add(new_badge)
        await session.commit()
        badge = await session.execute(
            select(Badge).filter_by(
                name=name, emoji=emoji
            )
        )
        return badge.scalar()


async def update_badge(
        badge_id: int,
        column_name: Literal[
            "id",
            "name",
            "emoji",
            "description",
            "link",
            "allowed_guilds",
            "is_global"
        ],
        value
) -> None:
    async with SessionLocal() as session:
        badge = await session.execute(
            select(Badge).filter_by(id=badge_id)
        )
        if badge:
            badge = badge.scalar()
            setattr(badge, column_name, value)
            await session.commit()


async def delete_badge(badge_id: int):
    async with SessionLocal() as session:
        badge = await session.execute(
            select(Badge).filter_by(id=badge_id)
        )
        if badge:
            badge = badge.scalar()
            await session.delete(badge)
            await session.commit()


async def if_badge_exists(
        name: str = None,
        emoji: str = None,
        badge_id: int = None,
        by_id: bool = False
) -> bool:
    async with SessionLocal() as session:
        if not by_id:
            badge = await session.execute(
                select(Badge).filter_by(
                    name=name, emoji=emoji
                )
            )
        else:
            badge = await session.execute(
                select(Badge).filter_by(
                    id=badge_id
                )
            )

        return badge.scalar() is not None


async def get_badge(badge_id: int):
    async with SessionLocal() as session:
        badge = await session.execute(
            select(Badge).filter_by(id=badge_id)
        )
        return badge.scalar()


async def get_all_badges():
    async with SessionLocal() as session:
        badges = await session.execute(select(Badge))
        return badges.scalars().all()


async def add_awarded_badge(
        maker_id: int,
        badge_id: int,
        awarder_id: int | None = None
):
    new_awarded_badge = AwardedBadge(
        maker_id=maker_id,
        badge_id=badge_id,
        awarder_id=awarder_id
    )
    async with SessionLocal() as session:
        session.add(new_awarded_badge)
        await session.commit()


async def delete_awarded_badge(maker_id: int, badge_id: int):
    async with SessionLocal() as session:
        awarded_badge = await session.execute(
            select(AwardedBadge).filter_by(maker_id=maker_id, badge_id=badge_id)
        )
        if awarded_badge:
            awarded_badge = awarded_badge.scalar()
            await session.delete(awarded_badge)
            await session.commit()


async def get_makers_awarded_badge(maker_id: int):
    async with SessionLocal() as session:
        awarded_badges = await session.execute(
            select(AwardedBadge).filter_by(maker_id=maker_id)
        )
        return awarded_badges.scalars().all()
