from email.utils import parsedate
from typing import Optional

import datetime

def try_parse_http_date(value: str) -> Optional[datetime.datetime]:
    timetuple = parsedate(value)
    if not timetuple:
        return None
    return datetime.datetime(*timetuple[:6], tzinfo=datetime.timezone.utc)
