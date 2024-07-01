from sqlalchemy import select

from ..database import SessionLocal
from ..models import MakerLog


async def add_log(maker_id: int, log: str):
    new_log = MakerLog(maker_id=maker_id, log=log)

    async with SessionLocal() as session:
        session.add(new_log)
        await session.commit()


async def get_maker_logs(maker_id: int) -> list[MakerLog]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(MakerLog).filter_by(maker_id=maker_id).order_by(MakerLog.timestamp.desc()))
        return result.scalars().all()
