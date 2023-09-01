from utils.databases.main_db import MainDataBase, PublicationsTable
from utils.html.templates.maker_log_template import maker_log_template
from utils.utilities import get_level_title, get_status_title

makers_db = MainDataBase()
pubs_db = PublicationsTable()


async def html_makers_actions_generator(
    data: list[tuple], date_start: str = None, date_end: str = None
):
    actions = []
    for action in data:
        action_id = action[0]

        if action[1] == "NULL":
            maker_nickname = "неизвестно"
            maker_discord_id = "неизвестно"
        else:
            maker = await makers_db.get_maker_by_id(id=action[1])
            maker_nickname = maker[2]
            maker_discord_id = maker[1]
            maker_id = maker[0]

        if action[2] == "NULL":
            madeby_nickname = "неизвестно"
            madeby_discord_id = "неизвестно"
        else:
            made_by = await makers_db.get_maker_by_id(id=action[2])
            madeby_nickname = made_by[2]
            madeby_discord_id = made_by[1]

        datetime = action[5]
        meta = action[4]
        reason = action[6]
        action_type = action[3]

        if action_type == "addmaker":
            log = f"{madeby_nickname} [{madeby_discord_id}] зарегистрировал/активировал аккаунт редактору {meta} [{maker_discord_id}]"
        elif action_type == "deactivate":
            log = f"{madeby_nickname} [{madeby_discord_id}] деактивировал аккаунт редактора {maker_nickname} [{maker_discord_id}]. Причина: {reason}"
        elif action_type == "setnickname":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил никнейм {meta} редактору с [{maker_discord_id}]"
        elif action_type == "setdiscord":
            log = f"{madeby_nickname} [{madeby_discord_id}] сменил Discord редактору с [ID: {maker_id}] с {maker_discord_id} на {meta}"
        elif action_type == "setlevel":
            level_title = await get_level_title(levelnum=int(meta))
            log = f"{madeby_nickname} [{madeby_discord_id}] установил редактору {maker_nickname} [{maker_discord_id}] {meta} уровень [{level_title}]"
        elif action_type == "setstatus":
            status_title = await get_status_title(status_kw=meta)
            log = f"{madeby_nickname} [{madeby_discord_id}] установил редактору {maker_nickname} [{maker_discord_id}] статус {meta} [{status_title}]"
        elif action_type == "warn":
            log = f"{madeby_nickname} [{madeby_discord_id}] выдал выговор редактору {maker_nickname} [{maker_discord_id}]. Причина: {reason}"
        elif action_type == "unwarn":
            log = f"{madeby_nickname} [{madeby_discord_id}] снял выговор редактору {maker_nickname} [{maker_discord_id}]. Причина: {reason}"
        else:
            log = "Ошибка в базе данных. Неизвестный тип действия."

        action_log = (action_id, log, datetime)
        actions.append(action_log)

    if (not date_start) and (not date_end):
        title = "Логи мейкеров за всё время"
    elif (date_start) and (not date_end):
        title = f"Логи мейкеров с {date_start} до настоящего времени"
    elif (date_start) and (date_end):
        title = f"Логи мейкеров с {date_start} до {date_end}"

    html_code = maker_log_template.render(title=title, actions=actions)
    return html_code
