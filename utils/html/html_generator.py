import jinja2
from utils.databases.main_db import MainDataBase, PublicationsTable
from utils.html.templates.logs_template import logs_template
from utils.utilities import get_level_title, get_status_title
from json import loads

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

    html_code = logs_template.render(title=title, actions=actions)
    return html_code


async def html_pubs_actions_generator(
    data: list[tuple], date_start: str = None, date_end: str = None
):
    actions = []
    for action in data:
        action_id = action[0]

        if action[1] == "NULL":
            pub_id = "неизвестно"
        else:
            pub_id = action[1]

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

        if action_type == "createpub":
            meta_list = loads(meta)
            date = meta_list[0]
            amount_dp = meta_list[1]
            log = f"{madeby_nickname} [{madeby_discord_id}] создал выпуск #{pub_id} с датой {date} и суммой DP {amount_dp}"
        elif action_type == "deletepub":
            log = f"{madeby_nickname} [{madeby_discord_id}] удалил выпуск #{meta}"
        elif action_type == "setpub_id":
            log = f"{madeby_nickname} [{madeby_discord_id}] изменил ID выпуска #{meta} на #{pub_id}"
        elif action_type == "setpub_date":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил дату выпуска #{pub_id} на {meta}"
        elif action_type == "setpub_maker":
            maker = await makers_db.get_maker_by_id(id=meta)
            maker_nickname = maker[2]
            maker_discord_id = maker[1]
            log = f"{madeby_nickname} [{madeby_discord_id}] назначил автором выпуска #{pub_id} редактора {maker_nickname} [{maker_discord_id}]"
        elif action_type == "setpub_status":
            status_title = await get_status_title(status_kw=meta)
            log = f"{madeby_nickname} [{madeby_discord_id}] установил выпуску #{pub_id} статус {meta} [{status_title}]"
        elif action_type == "setpub_amount":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил кол-во DP на {meta} за выпуск #{pub_id}"
        elif action_type == "setpub_infocreator":
            maker = await makers_db.get_maker_by_id(id=meta)
            maker_nickname = maker[2]
            maker_discord_id = maker[1]
            log = f"{madeby_nickname} [{madeby_discord_id}] установил {maker_nickname} [{maker_discord_id}] автором информации к выпуску #{pub_id}"
        elif action_type == "setpub_salarypayer":
            maker = await makers_db.get_maker_by_id(id=meta)
            maker_nickname = maker[2]
            maker_discord_id = maker[1]
            log = f"{madeby_nickname} [{madeby_discord_id}] установил человека, выплатившего DP за выпуск #{pub_id} на {maker_nickname} [{maker_discord_id}]"
        else:
            log = "Ошибка в базе данных. Неизвестный тип действия."

        action_log = (action_id, log, datetime)
        actions.append(action_log)

    if (not date_start) and (not date_end):
        title = "Логи выпусков за всё время"
    elif (date_start) and (not date_end):
        title = f"Логи выпусков с {date_start} до настоящего времени"
    elif (date_start) and (date_end):
        title = f"Логи выпусков с {date_start} до {date_end}"

    html_code = logs_template.render(title=title, actions=actions)
    return html_code
