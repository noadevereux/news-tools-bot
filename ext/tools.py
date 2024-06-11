import re


def get_status_title(status_kw: str | None) -> str:
    match status_kw:
        case "active":
            return "Активен"
        case "inactive":
            return "Неактивен"
        case "in_process":
            return "В процессе"
        case "completed":
            return "Сделан"
        case "failed":
            return "Провален"
        case None:
            return "Не установлено"
        case _:
            return "Неизвестно"


def validate_date(date_string: str):
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    if date_pattern.match(date_string):
        return True
    else:
        return False


def validate_url(url: str, /):
    url_pattern = re.compile(r"^https://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(:[0-9]{1,5})?(/.*)?$")

    if url_pattern.match(url):
        return True
    else:
        return False
