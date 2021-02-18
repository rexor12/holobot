from email.utils import parsedate

import datetime

def try_parse_http_date(value: str) -> datetime.datetime or None:
    timetuple = parsedate(value)
    if timetuple is None:
        return None
    return datetime(*timetuple[:6], tzinfo=datetime.timezone.utc)

def try_parse_int(value: str) -> int or None:
    try:
        return int(value)
    except ValueError:
        return None