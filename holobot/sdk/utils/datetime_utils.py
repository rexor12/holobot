import zoneinfo
from datetime import datetime, tzinfo

UTC: zoneinfo.ZoneInfo = zoneinfo.ZoneInfo("UTC")

def set_time_zone(dt: datetime, tz: tzinfo | None) -> datetime:
    return dt.replace(tzinfo=tz)

def set_time_zone_nullable(dt: datetime | None, tz: tzinfo | None) -> datetime | None:
    return dt.replace(tzinfo=tz) if dt else None
