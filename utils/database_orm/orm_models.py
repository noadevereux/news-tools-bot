from typing import Literal
from sqlalchemy import BigInteger, Column, Date, ForeignKey, TIMESTAMP, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_number: Mapped[int] = mapped_column(unique=True)
    maker_id: Mapped[int] = mapped_column(ForeignKey("makers.id"), nullable=True)
    date = Column(Date(), nullable=True)
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


class Maker(Base):
    __tablename__ = "makers"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True)
    level: Mapped[Literal["-1", "1", "2", "3", "4"]] = mapped_column(server_default="1")
    status: Mapped[Literal["new", "active", "inactive"]] = mapped_column(
        server_default="new"
    )
    warns: Mapped[int] = mapped_column(server_default="0")
    appointment_datetime = Column(TIMESTAMP(timezone=True), server_default=func.now())
    account_status: Mapped[bool] = mapped_column(server_default="1")

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
            "warn",
            "unwarn",
        ]
    ] = mapped_column()
    meta: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
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
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
