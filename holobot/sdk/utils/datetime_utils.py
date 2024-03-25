from datetime import datetime, time, timedelta, timezone, tzinfo

_MIDNIGHT = time()

def set_time_zone(dt: datetime, tz: tzinfo | None) -> datetime:
    return dt.replace(tzinfo=tz)

def set_time_zone_nullable(dt: datetime | None, tz: tzinfo | None) -> datetime | None:
    return dt.replace(tzinfo=tz) if dt else None

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def today_midnight_utc() -> datetime:
    today = utcnow().date()
    return datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

def get_last_day_of_week(day_of_week: int) -> datetime:
    today = utcnow().date()
    last_day_of_week = (
        today - timedelta(days=today.weekday() - day_of_week)
        if today.weekday() >= day_of_week
        else today + timedelta(days=day_of_week - today.weekday(), weeks=-1)
    )
    return datetime.combine(last_day_of_week, _MIDNIGHT, timezone.utc)

def get_next_day_of_week(day_of_week: int) -> datetime:
    today = utcnow().date()
    next_day_of_week = (
        today + timedelta(days=day_of_week - today.weekday(), weeks=1)
        if today.weekday() >= day_of_week
        else today + timedelta(days=day_of_week - today.weekday())
    )
    return datetime.combine(next_day_of_week, _MIDNIGHT, timezone.utc)
