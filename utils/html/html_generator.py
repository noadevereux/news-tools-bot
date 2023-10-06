import ast
from utils.database_orm import methods
from utils.database_orm.orm_models import MakerAction, PublicationAction
from utils.html.templates.logs_template import logs_template
from utils.utilities import get_level_title, get_status_title


async def html_makers_actions_generator(
    data: list[MakerAction], date_start: str = None, date_end: str = None
):
    actions = []
    for action in data:
        action_id = action.id

        if not action.maker_id:
            maker_nickname = "неизвестно"
            maker_discord_id = "неизвестно"
            maker_id = "неизвестно"
        else:
            maker = methods.get_maker_by_id(id=action.maker_id)

            if maker:
                maker_nickname = maker.nickname
                maker_discord_id = maker.discord_id
                maker_id = maker.id
            else:
                maker_nickname = "неизвестно"
                maker_discord_id = "неизвестно"
                maker_id = "неизвестно"

        if not action.made_by:
            madeby_nickname = "неизвестно"
            madeby_discord_id = "неизвестно"
        else:
            made_by = methods.get_maker_by_id(id=action.made_by)

            if made_by:
                madeby_nickname = made_by.nickname
                madeby_discord_id = made_by.discord_id
            else:
                madeby_nickname = "неизвестно"
                madeby_discord_id = "неизвестно"

        datetime = action.timestamp
        meta = action.meta
        reason = action.reason
        action_type = action.action

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
        elif action_type == "setdate":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил редактору {maker_nickname} [{maker_discord_id}] дату постановления на {meta}"
        elif action_type == "warn":
            log = f"{madeby_nickname} [{madeby_discord_id}] выдал выговор редактору {maker_nickname} [{maker_discord_id}]. Причина: {reason}"
        elif action_type == "unwarn":
            log = f"{madeby_nickname} [{madeby_discord_id}] снял выговор редактору {maker_nickname} [{maker_discord_id}]. Причина: {reason}"
        else:
            log = "<== Ошибка в базе данных. Неизвестный тип действия ==>"

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
    data: list[PublicationAction], date_start: str = None, date_end: str = None
):
    actions = []
    for action in data:
        action_id = action.id

        if not action.publication_id:
            pub_id = "неизвестно"
        else:
            pub = methods.get_publication_by_id(id=action.publication_id)
            if not pub:
                pub_id = "неизвестно"
            else:
                pub_id = pub.publication_number

        if not action.made_by:
            madeby_nickname = "неизвестно"
            madeby_discord_id = "неизвестно"
        else:
            made_by = methods.get_maker_by_id(id=action.made_by)
            madeby_nickname = made_by.nickname
            madeby_discord_id = made_by.discord_id

        datetime = action.timestamp
        meta = action.meta
        reason = action.reason
        action_type = action.action

        if action_type == "createpub":
            log = f"{madeby_nickname} [{madeby_discord_id}] создал выпуск #{pub_id}"
        elif action_type == "deletepub":
            log = f"{madeby_nickname} [{madeby_discord_id}] удалил выпуск #{meta}"
        elif action_type == "setpub_id":
            meta_list: list = ast.literal_eval(meta)
            old_number = meta_list[0]
            new_number = meta_list[1]
            log = f"{madeby_nickname} [{madeby_discord_id}] изменил ID выпуска #{old_number} на #{new_number}"
        elif action_type == "setpub_date":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил дату выпуска #{pub_id} на {meta}"
        elif action_type == "setpub_maker":
            maker = methods.get_maker_by_id(id=meta)
            maker_nickname = maker.nickname
            maker_discord_id = maker.discord_id
            log = f"{madeby_nickname} [{madeby_discord_id}] назначил автором выпуска #{pub_id} редактора {maker_nickname} [{maker_discord_id}]"
        elif action_type == "setpub_status":
            status_title = await get_status_title(status_kw=meta)
            log = f"{madeby_nickname} [{madeby_discord_id}] установил выпуску #{pub_id} статус {meta} [{status_title}]"
        elif action_type == "setpub_amount":
            log = f"{madeby_nickname} [{madeby_discord_id}] установил кол-во DP на {meta} за выпуск #{pub_id}"
        elif action_type == "setpub_infocreator":
            maker = methods.get_maker_by_id(id=meta)
            maker_nickname = maker.nickname
            maker_discord_id = maker.discord_id
            log = f"{madeby_nickname} [{madeby_discord_id}] установил {maker_nickname} [{maker_discord_id}] автором информации к выпуску #{pub_id}"
        elif action_type == "setpub_salarypayer":
            maker = methods.get_maker_by_id(id=meta)
            maker_nickname = maker.nickname
            maker_discord_id = maker.discord_id
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
