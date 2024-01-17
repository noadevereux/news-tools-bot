from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.sql import select

from api.auth.auth_bearer import JWTBearer
from ext.database import models
from ext.database.database import SessionLocal

db_router = APIRouter()


@db_router.get(
    "/is_maker_exists", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def is_maker_exists(guild_id: int, discord_id: int):
    async with SessionLocal() as session:
        maker = await session.execute(
            select(models.Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
        result = maker.scalar()

    return {"status": "ok", "message": (result is not None)}


@db_router.get(
    "/is_maker_exists_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker"],
)
async def is_maker_exists_by_id(id: int):
    async with SessionLocal() as session:
        maker = await session.execute(select(models.Maker).filter_by(id=id))
        result = maker.scalar()

    return {"status": "ok", "message": (result is not None)}


@db_router.post(
    "/add_maker", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def add_maker(guild_id: int, discord_id: int, nickname: str):
    new_maker = models.Maker(
        guild_id=guild_id, discord_id=discord_id, nickname=nickname
    )
    async with SessionLocal() as session:
        session.add(new_maker)
        await session.commit()
        maker = await session.execute(
            select(models.Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )

    return {"status": "ok", "maker": maker.scalar()}


@db_router.post(
    "/update_maker", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def update_maker(
    guild_id: int,
    discord_id: int,
    column_name: Literal[
        "id",
        "guild_id",
        "discord_id",
        "nickname",
        "level",
        "post_name",
        "status",
        "warns",
        "preds",
        "appointment_datetime",
        "account_status",
    ],
    value,
):
    match value:
        case "false":
            value = False
        case "true":
            value = True
        case "null":
            value = None

    async with SessionLocal() as session:
        maker = await session.execute(
            select(models.Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.post(
    "/update_maker_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker"],
)
async def update_maker_by_id(
    id: int,
    column_name: Literal[
        "id",
        "guild_id",
        "discord_id",
        "nickname",
        "level",
        "post_name",
        "status",
        "warns",
        "preds",
        "appointment_datetime",
        "account_status",
    ],
    value,
):
    match value:
        case "false":
            value = False
        case "true":
            value = True
        case "null":
            value = None

    async with SessionLocal() as session:
        maker = await session.execute(select(models.Maker).filter_by(id=id))
        if maker:
            maker = maker.scalar()
            setattr(maker, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.get(
    "/get_all_makers", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def get_all_makers(guild_id: int):
    async with SessionLocal() as session:
        makers_list = await session.execute(
            select(models.Maker).filter_by(guild_id=guild_id)
        )

    return {"status": "ok", "makers": makers_list.scalars().all()}


@db_router.get(
    "/get_all_makers_sorted",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker"],
)
async def get_all_makers_sorted(guild_id: int):
    async with SessionLocal() as session:
        makers_list = await session.execute(
            select(models.Maker)
            .filter_by(guild_id=guild_id)
            .order_by(models.Maker.level.desc())
        )

    return {"status": "ok", "makers": makers_list.scalars().all()}


@db_router.get(
    "/get_maker", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def get_maker(guild_id: int, discord_id: int):
    async with SessionLocal() as session:
        maker = await session.execute(
            select(models.Maker).filter_by(guild_id=guild_id, discord_id=discord_id)
        )

    return {"status": "ok", "maker": maker.scalar()}


@db_router.get(
    "/get_maker_accounts",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker"],
)
async def get_maker_accounts(discord_id: int):
    async with SessionLocal() as session:
        accounts = await session.execute(
            select(models.Maker).filter_by(discord_id=discord_id)
        )

    return {"status": "ok", "makers": accounts.scalars().all()}


@db_router.get(
    "/get_maker_by_id", dependencies=[Depends(JWTBearer())], tags=["Database", "Maker"]
)
async def get_maker_by_id(id: int):
    async with SessionLocal() as session:
        maker = await session.execute(select(models.Maker).filter_by(id=id))

    return {"status": "ok", "maker": maker.scalar()}


@db_router.get(
    "/get_publications_by_maker",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker"],
)
async def get_publications_by_maker(id: int):
    async with SessionLocal() as session:
        publications_list = await session.execute(
            select(models.Publication).filter_by(maker_id=id, status="completed")
        )

    return {"status": "ok", "publications": publications_list.scalars().all()}


@db_router.post(
    "/add_maker_action",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker Actions"],
)
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
        "setdate",
        "warn",
        "unwarn",
        "pred",
        "unpred",
    ],
    meta: str = None,
    reason: str = None,
):
    new_action = models.MakerAction(
        maker_id=maker_id, made_by=made_by, action=action, meta=meta, reason=reason
    )
    async with SessionLocal() as session:
        session.add(new_action)
        await session.commit()

    return {"status": "ok", "message": None}


@db_router.get(
    "/get_maker_actions",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Maker Actions"],
)
async def get_makers_actions(maker_id: int):
    async with SessionLocal() as session:
        actions = await session.execute(
            select(models.MakerAction)
            .filter_by(maker_id=maker_id)
            .order_by(models.MakerAction.timestamp.desc())
        )

    return {"status": "ok", "actions": actions.scalars().all()}


@db_router.post(
    "/add_publication",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def add_publication(guild_id: int, publication_number: int):
    new_publication = models.Publication(
        guild_id=guild_id, publication_number=publication_number
    )
    async with SessionLocal() as session:
        session.add(new_publication)
        await session.commit()
        publication = await session.execute(
            select(models.Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )

    return {"status": "ok", "publication": publication.scalar()}


@db_router.post(
    "/update_publication",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
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
    value,
):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        if publication:
            publication = publication.scalar()
            setattr(publication, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.post(
    "/update_publication_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
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
    value,
):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(id=publication_id)
        )
        if publication:
            publication = publication.scalar()

            if value == "null":
                value = None

            setattr(publication, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.delete(
    "/delete_publication",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def delete_publication(guild_id: int, publication_number: int):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        if publication:
            publication = publication.scalar()
            await session.delete(publication)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.delete(
    "/delete_publication_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def delete_publication_by_id(publication_id: int):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(id=publication_id)
        )
        if publication:
            publication = publication.scalar()
            await session.delete(publication)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.get(
    "/is_publication_exists",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def is_publication_exists(guild_id: int, publication_number: int):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )
        result = publication.scalar()

    return {"status": "ok", "message": (result is not None)}


@db_router.get(
    "/get_publication",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def get_publication(guild_id: int, publication_number: int):
    async with SessionLocal() as session:
        publication = await session.execute(
            select(models.Publication).filter_by(
                guild_id=guild_id, publication_number=publication_number
            )
        )

    return {"status": "ok", "publication": publication.scalar()}


@db_router.get(
    "/get_publication_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def get_publication(id: int):
    async with SessionLocal() as session:
        publication = await session.execute(select(models.Publication).filter_by(id=id))

    return {"status": "ok", "publication": publication.scalar()}


@db_router.get(
    "/get_all_publications",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication"],
)
async def get_publication(guild_id: int):
    async with SessionLocal() as session:
        publications_list = await session.execute(
            select(models.Publication).filter_by(guild_id=guild_id)
        )

    return {"status": "ok", "publications": publications_list.scalars().all()}


@db_router.post(
    "/add_pub_action",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication Actions"],
)
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
):
    new_action = models.PublicationAction(
        publication_id=pub_id, made_by=made_by, action=action, meta=meta, reason=reason
    )

    async with SessionLocal() as session:
        session.add(new_action)
        await session.commit()

    return {"status": "ok", "message": None}


@db_router.get(
    "/get_pubs_actions",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication Actions"],
)
async def get_pubs_actions(pub_id: int):
    async with SessionLocal() as session:
        actions = await session.execute(
            select(models.PublicationAction)
            .filter_by(publication_id=pub_id)
            .order_by(models.PublicationAction.timestamp.desc())
        )

    return {"status": "ok", "actions": actions.scalars().all()}


@db_router.get(
    "/get_all_pub_actions",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Publication Actions"],
)
async def get_all_pub_actions():
    async with SessionLocal() as session:
        actions = await session.execute(
            select(models.PublicationAction).order_by(
                models.PublicationAction.timestamp.desc()
            )
        )

    return {"status": "ok", "actions": actions.scalars().all()}


@db_router.post(
    "/add_guild", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def add_guild(discord_id: int, guild_name: str):
    guild = models.Guild(discord_id=discord_id, guild_name=guild_name)
    async with SessionLocal() as session:
        session.add(guild)
        await session.commit()

    return {"status": "ok", "message": None}


@db_router.get(
    "/is_guild_exists", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def is_guild_exists(discord_id: int):
    async with SessionLocal() as session:
        guild = await session.execute(
            select(models.Guild).filter_by(discord_id=discord_id)
        )
        result = guild.scalar()

    return {"status": "ok", "message": (result is not None)}


@db_router.get(
    "/get_guild", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def get_guild(discord_id: int):
    async with SessionLocal() as session:
        guild = await session.execute(
            select(models.Guild).filter_by(discord_id=discord_id)
        )
        result = guild.scalar()

    return {"status": "ok", "guild": result}


@db_router.get(
    "/get_guild_by_id", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def get_guild_by_id(id: int):
    async with SessionLocal() as session:
        guild = await session.execute(select(models.Guild).filter_by(id=id))
        result = guild.scalar()

    return {"status": "ok", "guild": result}


@db_router.get(
    "/get_all_guilds", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def get_all_guilds():
    async with SessionLocal() as session:
        guild = await session.execute(select(models.Guild))
        result = guild.scalars().all()

    return {"status": "ok", "guilds": result}


@db_router.post(
    "/update_guild", dependencies=[Depends(JWTBearer())], tags=["Database", "Guilds"]
)
async def update_guild(
    discord_id: int,
    column_name: Literal[
        "id",
        "discord_id",
        "guild_name",
        "roles_list",
        "is_notifies_enabled",
        "channel_id",
        "is_admin_guild",
        "is_active",
    ],
    value,
):
    async with SessionLocal() as session:
        guild = await session.execute(
            select(models.Guild).filter_by(discord_id=discord_id)
        )
        if guild:
            guild = guild.scalar()
            setattr(guild, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}


@db_router.post(
    "/update_guild_by_id",
    dependencies=[Depends(JWTBearer())],
    tags=["Database", "Guilds"],
)
async def update_guild_by_id(
    id: int,
    column_name: Literal[
        "id",
        "discord_id",
        "guild_name",
        "roles_list",
        "is_notifies_enabled",
        "channel_id",
        "is_admin_guild",
        "is_active",
    ],
    value,
):
    async with SessionLocal() as session:
        guild = await session.execute(select(models.Guild).filter_by(id=id))
        if guild:
            guild = guild.scalar()
            setattr(guild, column_name, value)
            await session.commit()

    return {"status": "ok", "message": None}
