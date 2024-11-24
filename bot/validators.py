import re
from datetime import datetime


def is_valid_fio(fio):
    return bool(re.match(r'^[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+$', fio.strip()))


def is_valid_group(group):
    return bool(re.match(r'^МЕН-\d{6}$', group))


def is_valid_date(date_str):
    try:
        date = datetime.strptime(date_str, "%d.%m.%Y")
        return date <= datetime.now()
    except ValueError:
        return False


def is_valid_task(task):
    return bool(re.match(r'^\d+$', task))
