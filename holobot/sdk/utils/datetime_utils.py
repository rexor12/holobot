from datetime import datetime, tzinfo
from typing import Optional

import zoneinfo

UTC: zoneinfo.ZoneInfo = zoneinfo.ZoneInfo("UTC")

def set_time_zone(dt: datetime, tz: Optional[tzinfo]) -> datetime:
    return dt.replace(tzinfo=tz)

def set_time_zone_nullable(dt: Optional[datetime], tz: Optional[tzinfo]) -> Optional[datetime]:
    return dt.replace(tzinfo=tz) if dt else None
