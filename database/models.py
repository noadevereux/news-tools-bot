from datetime import datetime, date
from typing import Literal, List

from sqlalchemy import BigInteger, Date, ForeignKey, TIMESTAMP, String, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func

from .database import engine


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"))
    publication_number: Mapped[int] = mapped_column()
    maker_id: Mapped[int] = mapped_column(ForeignKey("makers.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date(), nullable=True)
    information_creator_id: Mapped[int] = mapped_column(
        ForeignKey("makers.id"), nullable=True
    )
    status: Mapped[Literal["in_process", "completed", "failed"]] = mapped_column(
        server_default="in_process"
    )
    amount_dp: Mapped[float] = mapped_column(nullable=True)
    salary_payer_id: Mapped[int] = mapped_column(ForeignKey("makers.id"), nullable=True)

    maker: Mapped["Maker"] = relationship(
        back_populates="publications_made",
        foreign_keys=[maker_id],
        primaryjoin="Publication.maker_id == Maker.id",
        lazy="select"
    )

    information_creator: Mapped["Maker"] = relationship(
        back_populates="publications_created",
        foreign_keys=[information_creator_id],
        primaryjoin="Publication.information_creator_id == Maker.id",
        lazy="select"
    )

    salary_payer: Mapped["Maker"] = relationship(
        back_populates="publications_paid",
        foreign_keys=[salary_payer_id],
        primaryjoin="Publication.salary_payer_id == Maker.id",
        lazy="select"
    )

    guild: Mapped["Guild"] = relationship(
        back_populates="publications",
        foreign_keys=[guild_id],
        primaryjoin="Publication.guild_id == Guild.id",
        lazy="select"
    )


class AwardedBadge(Base):
    __tablename__ = "awarded_badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    maker_id: Mapped[int] = mapped_column(ForeignKey("makers.id"))
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"))
    awarder_id: Mapped[int] = mapped_column(ForeignKey("makers.id"), nullable=True)
    award_timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    badge: Mapped["Badge"] = relationship(back_populates="awarded_badges", lazy="select")
    maker: Mapped["Maker"] = relationship(
        back_populates="awarded_badges",
        foreign_keys=[maker_id],
        primaryjoin="AwardedBadge.maker_id == Maker.id",
        lazy="select"
    )
    awarder: Mapped["Maker"] = relationship(
        back_populates="awards_badges",
        foreign_keys=[awarder_id],
        primaryjoin="AwardedBadge.awarder_id == Maker.id",
        lazy="select"
    )


class Maker(Base):
    __tablename__ = "makers"

    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"))
    discord_id: Mapped[int] = mapped_column(BigInteger)
    nickname: Mapped[str] = mapped_column(String(255))
    level: Mapped[Literal["0", "1", "2", "3", "4", "5"]] = mapped_column(
        server_default="1"
    )
    post_name: Mapped[str] = mapped_column(
        String(255), nullable=True, server_default="Редактор"
    )
    status: Mapped[Literal["new", "active", "inactive"]] = mapped_column(
        server_default="active"
    )
    warns: Mapped[int] = mapped_column(server_default="0")
    preds: Mapped[int] = mapped_column(server_default="0")
    appointment_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    is_admin: Mapped[bool] = mapped_column(server_default="0")
    account_status: Mapped[bool] = mapped_column(server_default="1")

    guild: Mapped["Guild"] = relationship(
        back_populates="makers",
        foreign_keys=[guild_id],
        primaryjoin="Maker.guild_id == Guild.id",
        lazy="select"
    )

    publications_made: Mapped["Publication"] = relationship(
        back_populates="maker",
        foreign_keys=[Publication.maker_id],
        primaryjoin="Maker.id == Publication.maker_id",
        lazy="select"
    )

    publications_created: Mapped["Publication"] = relationship(
        back_populates="information_creator",
        foreign_keys=[Publication.information_creator_id],
        primaryjoin="Maker.id == Publication.information_creator_id",
        lazy="select"
    )

    publications_paid: Mapped["Publication"] = relationship(
        back_populates="salary_payer",
        foreign_keys=[Publication.salary_payer_id],
        primaryjoin="Maker.id == Publication.salary_payer_id",
        lazy="select"
    )

    awarded_badges: Mapped[List["AwardedBadge"]] = relationship(
        back_populates="maker",
        foreign_keys=[AwardedBadge.maker_id],
        primaryjoin="Maker.id == AwardedBadge.maker_id",
        lazy="select"
    )
    awards_badges: Mapped[List["AwardedBadge"]] = relationship(
        back_populates="awarder",
        foreign_keys=[AwardedBadge.awarder_id],
        primaryjoin="Maker.id == AwardedBadge.awarder_id",
        lazy="select"
    )


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    guild_name: Mapped[str] = mapped_column(String(255), unique=True)
    duty_role_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    roles_list: Mapped[list[str]] = mapped_column(JSON, default=[])
    is_notifies_enabled: Mapped[bool] = mapped_column(server_default="1")
    channel_id: Mapped[int] = mapped_column(
        BigInteger, nullable=True, server_default=None
    )
    log_roles_list: Mapped[list[str]] = mapped_column(JSON, default=[])
    log_roles_channel: Mapped[int] = mapped_column(
        BigInteger, nullable=True, server_default=None
    )
    is_admin_guild: Mapped[bool] = mapped_column(server_default="0")
    is_active: Mapped[bool] = mapped_column(server_default="1")

    publications: Mapped[List["Publication"]] = relationship(
        back_populates="guild",
        foreign_keys=[Publication.guild_id],
        primaryjoin="Guild.id == Publication.guild_id",
        lazy="select"
    )

    makers: Mapped[List["Maker"]] = relationship(
        back_populates="guild",
        foreign_keys=[Maker.guild_id],
        primaryjoin="Guild.id == Maker.guild_id",
        lazy="select"
    )


class MakerLog(Base):
    __tablename__ = "maker_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    maker_id: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=func.now(), nullable=False)
    log: Mapped[str] = mapped_column(String(2000), nullable=False)


class PublicationAction(Base):
    __tablename__ = "publication_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(nullable=True)
    made_by: Mapped[int] = mapped_column(nullable=True)
    action: Mapped[
        Literal[
            "createpub",
            "deletepub",
            "setpub_id",
            "setpub_date",
            "setpub_maker",
            "setpub_status",
            "setpub_amount",
            "setpub_infocreator",
            "setpub_salarypayer",
        ]
    ] = mapped_column()
    meta: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=True)


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    emoji: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(4000), nullable=True)
    link: Mapped[str] = mapped_column(String(255), nullable=True)
    allowed_guilds: Mapped[list] = mapped_column(JSON(), default=[])
    is_global: Mapped[bool] = mapped_column(server_default="1")

    awarded_badges: Mapped[List["AwardedBadge"]] = relationship(back_populates="badge", lazy="select")


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
