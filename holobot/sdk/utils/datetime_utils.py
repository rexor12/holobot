from datetime import datetime, timezone, tzinfo

def set_time_zone(dt: datetime, tz: tzinfo | None) -> datetime:
    return dt.replace(tzinfo=tz)

def set_time_zone_nullable(dt: datetime | None, tz: tzinfo | None) -> datetime | None:
    return dt.replace(tzinfo=tz) if dt else None

def utcnow():
    return datetime.now(timezone.utc)
