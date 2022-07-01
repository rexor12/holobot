from datetime import datetime, timezone
from email.utils import parsedate
from typing import Optional

def try_parse_http_date(value: str) -> Optional[datetime]:
    timetuple = parsedate(value)
    if not timetuple:
        return None
    return datetime(*timetuple[:6], tzinfo=timezone.utc)
