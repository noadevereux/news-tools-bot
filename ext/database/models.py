from typing import Literal
from sqlalchemy import BigInteger, Date, ForeignKey, TIMESTAMP, String, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func
from .database import engine
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime, date


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

    maker_rel = relationship(
        "Maker",
        back_populates="publications_made",
        foreign_keys=[maker_id],
        primaryjoin="Publication.maker_id == Maker.id",
    )

    information_creator_rel = relationship(
        "Maker",
        back_populates="publications_created",
        foreign_keys=[information_creator_id],
        primaryjoin="Publication.information_creator_id == Maker.id",
    )

    salary_payer_rel = relationship(
        "Maker",
        back_populates="publications_paid",
        foreign_keys=[salary_payer_id],
        primaryjoin="Publication.salary_payer_id == Maker.id",
    )

    guild_id_rel = relationship(
        "Guild",
        back_populates="publications",
        foreign_keys=[guild_id],
        primaryjoin="Publication.guild_id == Guild.id"
    )


class Maker(Base):
    __tablename__ = "makers"

    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"))
    discord_id: Mapped[int] = mapped_column(BigInteger)
    nickname: Mapped[str] = mapped_column(String(255))
    level: Mapped[Literal["0", "1", "2", "3", "4", "5"]] = mapped_column(server_default="1")
    post_name: Mapped[str] = mapped_column(String(255), nullable=True, server_default="Редактор")
    status: Mapped[Literal["new", "active", "inactive"]] = mapped_column(
        server_default="active"
    )
    warns: Mapped[int] = mapped_column(server_default="0")
    appointment_datetime: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    account_status: Mapped[bool] = mapped_column(server_default="1")

    guild_id_rel = relationship(
        "Guild",
        back_populates="makers",
        foreign_keys=[guild_id],
        primaryjoin="Maker.guild_id == Guild.id"
    )

    publications_made = relationship(
        "Publication",
        back_populates="maker_rel",
        foreign_keys=[Publication.maker_id],
        primaryjoin="Maker.id == Publication.maker_id",
    )

    publications_created = relationship(
        "Publication",
        back_populates="information_creator_rel",
        foreign_keys=[Publication.information_creator_id],
        primaryjoin="Maker.id == Publication.information_creator_id",
    )

    publications_paid = relationship(
        "Publication",
        back_populates="salary_payer_rel",
        foreign_keys=[Publication.salary_payer_id],
        primaryjoin="Maker.id == Publication.salary_payer_id",
    )


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    guild_name: Mapped[str] = mapped_column(String(255), unique=True)
    roles_list: Mapped[list[int]] = mapped_column(JSON, default="[]")
    is_notifies_enabled: Mapped[bool] = mapped_column(server_default="1")
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True, server_default=None)
    is_admin_guild: Mapped[bool] = mapped_column(server_default="0")
    is_active: Mapped[bool] = mapped_column(server_default="1")

    publications = relationship(
        "Publication",
        back_populates="guild_id_rel",
        foreign_keys=[Publication.guild_id],
        primaryjoin="Guild.id == Publication.guild_id"
    )

    makers = relationship(
        "Maker",
        back_populates="guild_id_rel",
        foreign_keys=[Maker.guild_id],
        primaryjoin="Guild.id == Maker.guild_id"
    )


class MakerAction(Base):
    __tablename__ = "maker_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    maker_id: Mapped[int] = mapped_column(nullable=True)
    made_by: Mapped[int] = mapped_column(nullable=True)
    action: Mapped[
        Literal[
            "addmaker",
            "deactivate",
            "setnickname",
            "setdiscord",
            "setlevel",
            "setstatus",
            "setdate",
            "warn",
            "unwarn",
        ]
    ] = mapped_column()
    meta: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    reason: Mapped[str] = mapped_column(String(255), nullable=True)


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
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    reason: Mapped[str] = mapped_column(String(255), nullable=True)


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
