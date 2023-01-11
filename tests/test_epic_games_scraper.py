import zoneinfo
from datetime import datetime, time, timedelta, timezone

EPIC_UPDATE_TIMEZONE = zoneinfo.ZoneInfo("US/Central") # US/Central is UTC-06:00
EPIC_UPDATE_DAYOFWEEK = 3
EPIC_UPDATE_TIME = time(hour=10)

def get_next_scrape_time(now: datetime, last_scrape_time: datetime | None) -> datetime:
    if last_scrape_time is None:
        return now - timedelta(minutes=1)

    today = now.astimezone(EPIC_UPDATE_TIMEZONE).date()
    time_to_nearest_release_day = timedelta(days=EPIC_UPDATE_DAYOFWEEK - today.weekday())
    if today.weekday() >= EPIC_UPDATE_DAYOFWEEK:
        previous_thursday = today - timedelta(days=today.weekday() - EPIC_UPDATE_DAYOFWEEK)
        next_thursday = today + timedelta(weeks=1) + time_to_nearest_release_day
    else:
        previous_thursday = today - timedelta(weeks=1) + time_to_nearest_release_day
        next_thursday = today + time_to_nearest_release_day
    execution_delay = timedelta(seconds=5 * 60)
    previous_release_time = datetime.combine(previous_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE) + execution_delay
    if last_scrape_time < previous_release_time:
        if now > previous_release_time:
            return now - timedelta(minutes=1)
        else:
            return previous_release_time.astimezone(timezone.utc)

    next_release_time = datetime.combine(next_thursday, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE)
    return next_release_time.astimezone(timezone.utc) + execution_delay

def are_equal(next_scrape_at: datetime, expected_value: datetime) -> bool:
    print(f"next_scrape_at: {next_scrape_at}, expected: {expected_value}")
    return next_scrape_at == expected_value

# Just released, last scraped after the previous release -> should scrape in 5 mins.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Just released, last scraped before the previous release -> should scrape in 5 mins (on the same day we wait for the new release).
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 5 mins, last scraped after the previous release -> should scrape in 10 mins.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 5 mins, last scraped before the previous release -> should scrape in 10 mins (on the same day we wait for the new release).
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 1 day, last scraped after the previous release -> should scrape in 1 day 5 mins.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 11, 16, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 1 day, last scraped before the previous release -> should scrape 1 min ago.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 11, 16, 0, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 11, 15, 59, tzinfo=timezone.utc)
)

# Released 5 mins ago, last scraped after the previous release -> should scrape now.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Released 5 mins ago, last scraped before the previous release -> should scrape now.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Released 10 mins ago, last scraped after the previous release -> should scrape 1 min ago.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 10, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 9, tzinfo=timezone.utc)
)

# Released 10 mins ago, last scraped before the previous release -> should scrape 1 min ago.
assert are_equal(
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 10, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 9, tzinfo=timezone.utc)
)
