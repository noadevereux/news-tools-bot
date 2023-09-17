from typing import Literal
from .orm_models import Maker, MakerAction, Publication, PublicationAction
from .database import SessionLocal

# BEGIN MAKERS METHODS


def is_maker_exists(discord_id: int) -> bool:
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(discord_id=discord_id).first()
    return maker is not None


def is_maker_exists_by_id(id: int) -> bool:
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(id=id).first()
    return maker is not None


def add_maker(discord_id: int, nickname: str) -> None:
    new_maker = Maker(discord_id=discord_id, nickname=nickname)
    with SessionLocal() as session:
        session.add(new_maker)
        session.commit()


def deactivate_maker(discord_id: int) -> None:
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(discord_id=discord_id).first()
        if maker:
            maker.account_status = False
            session.commit()


def update_maker(
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
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(discord_id=discord_id).first()
        if maker:
            setattr(maker, column_name, value)
            session.commit()


def update_maker_by_id(
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
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(id=id).first()
        if maker:
            setattr(maker, column_name, value)
            session.commit()


def get_all_makers() -> list[Maker] | None:
    with SessionLocal() as session:
        makers = session.query(Maker).all()
    return makers


def get_maker(discord_id: int) -> Maker | None:
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(discord_id=discord_id).first()
    return maker


def get_maker_by_id(id: int) -> Maker | None:
    with SessionLocal() as session:
        maker = session.query(Maker).filter_by(id=id).first()
    return maker


def get_publications_by_maker(id: int) -> list[Publication]:
    with SessionLocal() as session:
        publications = (
            session.query(Publication).filter_by(maker_id=id, status="completed").all()
        )
    return publications


# END MAKERS METHODS

# BEGIN PUBLICATIONS METHODS


def add_publication(publication_id: int) -> None:
    new_publication = Publication(publication_number=publication_id)
    with SessionLocal() as session:
        session.add(new_publication)
        session.commit()


def update_publication(
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
    value: int | str,
) -> None:
    with SessionLocal() as session:
        publication = (
            session.query(Publication)
            .filter_by(publication_number=publication_id)
            .first()
        )
        if publication:
            setattr(publication, column_name, value)
            session.commit()


def delete_publication(publication_id: int) -> None:
    with SessionLocal() as session:
        publication = (
            session.query(Publication)
            .filter_by(publication_number=publication_id)
            .first()
        )
        if publication:
            session.delete(publication)
            session.commit()


def is_publication_exists(publication_id: int) -> bool:
    with SessionLocal() as session:
        publication = (
            session.query(Publication)
            .filter_by(publication_number=publication_id)
            .first()
        )
    return publication is not None


def get_publication(publication_id: int) -> Publication | None:
    with SessionLocal() as session:
        publication = (
            session.query(Publication)
            .filter_by(publication_number=publication_id)
            .first()
        )
    return publication


def get_all_publications() -> list[Publication] | None:
    with SessionLocal() as session:
        publications = session.query(Publication).all()
    return publications


# END PUBLICATION METHODS

# BEGIN MAKER ACTIONS METHODS


def add_maker_action(
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

    with SessionLocal() as session:
        session.add(new_action)
        session.commit()


def get_makers_actions(maker_id: int) -> list[MakerAction]:
    with SessionLocal() as session:
        actions = (
            session.query(MakerAction)
            .filter_by(maker_id=maker_id)
            .order_by(MakerAction.timestamp.desc())
            .all()
        )
    return actions


def get_all_maker_actions() -> list[MakerAction]:
    with SessionLocal() as session:
        actions = (
            session.query(MakerAction).order_by(MakerAction.timestamp.desc()).all()
        )
    return actions


# END MAKER ACTIONS METHODS

# BEGIN PUBLICATION ACTIONS METHODS


def add_pub_action(
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
    meta: str = None,
    reason: str = None,
) -> None:
    new_action = PublicationAction(
        publication_id=pub_id, made_by=made_by, action=action, meta=meta, reason=reason
    )

    with SessionLocal() as session:
        session.add(new_action)
        session.commit()


def get_pubs_actions(pub_id: int) -> list[PublicationAction]:
    with SessionLocal() as session:
        actions = (
            session.query(PublicationAction)
            .filter_by(publication_id=pub_id)
            .order_by(PublicationAction.timestamp.desc())
            .all()
        )
    return actions


def get_all_pub_actions() -> list[PublicationAction]:
    with SessionLocal() as session:
        actions = (
            session.query(PublicationAction)
            .order_by(PublicationAction.timestamp.desc())
            .all()
        )
    return actions


# END PUBLICATION ACTIONS METHODS
