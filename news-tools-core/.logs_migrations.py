from asyncio import run

from database.database import SessionLocal
from database.models import MakerAction, MakerLog

from database.methods import (
    makers as maker_methods
)

from sqlalchemy import select

from ext.tools import get_status_title


async def run_migration():
    async with SessionLocal() as session:
        result = await session.execute(select(MakerAction).order_by(MakerAction.id.asc()))
        actions = result.scalars().all()

        for action in actions:
            action_id = action.id

            if not action.made_by:
                action.made_by = "#"
                madeby_nickname = "Неизвестно"
            elif action.made_by == -1:
                madeby_nickname = "Система"
            else:
                made_by = await maker_methods.get_maker_by_id(id=int(action.made_by))

                if made_by:
                    madeby_nickname = made_by.nickname
                else:
                    madeby_nickname = "Неизвестно"

            maker = await maker_methods.get_maker_by_id(id=action.maker_id)
            if maker:
                maker_nickname = maker.nickname
            else:
                maker_nickname = "Неизвестно"

            action_datetime_l = action.timestamp.isoformat().split("T")
            action_datetime = f"{action_datetime_l[0]} {action_datetime_l[1]}"
            meta = action.meta
            reason = action.reason
            action_type = action.action

            if action_type == "addmaker":
                log = f"{madeby_nickname} зарегистрировал/активировал аккаунт редактору {meta}"
            elif action_type == "deactivate":
                log = f"{madeby_nickname} деактивировал аккаунт редактора {maker_nickname}. Причина: {reason}"
            elif action_type == "setnickname":
                log = f"{madeby_nickname} установил редактору никнейм {meta}"
            elif action_type == "setdiscord":
                log = f"{madeby_nickname} установил Discord редактору {maker_nickname} на {meta}"
            elif action_type == "setlevel":
                log = (
                    f"{madeby_nickname} установил редактору {maker_nickname} {meta} уровень"
                )
            elif action_type == "setpost":
                log = f"{madeby_nickname} установил редактору {maker_nickname} должность {meta}"
            elif action_type == "setstatus":
                status_title = get_status_title(status_kw=meta)
                log = f"{madeby_nickname} установил редактору {maker_nickname} статус на {status_title}"
            elif action_type == "setdate":
                log = f"{madeby_nickname} установил редактору {maker_nickname} дату постановления на {meta}"
            elif action_type == "warn":
                log = f"{madeby_nickname} выдал выговор редактору {maker_nickname}. Причина: {reason}"
            elif action_type == "unwarn":
                log = f"{madeby_nickname} снял выговор редактору {maker_nickname}. Причина: {reason}"
            elif action_type == "pred":
                log = f"{madeby_nickname} выдал предупреждение редактору {maker_nickname}. Причина: {reason}"
            elif action_type == "unpred":
                log = f"{madeby_nickname} снял предупреждение редактору {maker_nickname}. Причина: {reason}"
            else:
                continue

            new_log = MakerLog(maker_id=action.maker_id, timestamp=action.timestamp, log=log)
            session.add(new_log)

        await session.commit()


if __name__ == "__main__":
    run(run_migration())
