from datetime import datetime, timezone
from email.utils import parsedate

def try_parse_http_date(value: str) -> datetime | None:
    timetuple = parsedate(value)
    if not timetuple:
        return None
    return datetime(*timetuple[:6], tzinfo=timezone.utc)
