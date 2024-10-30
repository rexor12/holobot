import zoneinfo
from datetime import datetime, time, timedelta, timezone

EPIC_UPDATE_TIMEZONE = zoneinfo.ZoneInfo("US/Central") # US/Central is UTC-06:00
EPIC_UPDATE_TIME = time(hour=10)
EXECUTION_DELAY = timedelta(seconds=5 * 60)

def get_next_scrape_time(now: datetime, last_scrape_time: datetime | None) -> datetime:
    if last_scrape_time is None:
        return now - timedelta(minutes=1)

    today = now.astimezone(EPIC_UPDATE_TIMEZONE).date()
    release_time_today = datetime.combine(today, EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE) + EXECUTION_DELAY
    if last_scrape_time < release_time_today:
        if now > release_time_today:
            return now - timedelta(minutes=1)
        return release_time_today.astimezone(timezone.utc)

    release_time_tomorrow = datetime.combine(today + timedelta(days=1), EPIC_UPDATE_TIME, EPIC_UPDATE_TIMEZONE) + EXECUTION_DELAY
    return release_time_tomorrow.astimezone(timezone.utc)

def are_equal(name: str, next_scrape_at: datetime, expected_value: datetime) -> bool:
    print(f"[{name}] next_scrape_at: {next_scrape_at}, expected: {expected_value}")
    return next_scrape_at == expected_value

# Just released, last scraped after the previous release -> should scrape in 5 mins.
assert are_equal(
    "Just released, last scraped after the previous release -> should scrape in 5 mins.",
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Just released, last scraped before the previous release -> should scrape in 5 mins (on the same day we wait for the new release).
assert are_equal(
    "Just released, last scraped before the previous release -> should scrape in 5 mins (on the same day we wait for the new release).",
    get_next_scrape_time(
        datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 5 mins, last scraped after the previous release -> should scrape in 10 mins.
assert are_equal(
    "Releases in 5 mins, last scraped after the previous release -> should scrape in 10 mins.",
    get_next_scrape_time(
        datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
        datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases in 5 mins, last scraped before the previous release -> should scrape in 10 mins (on the same day we wait for the new release).
assert are_equal(
    "Releases in 5 mins, last scraped before the previous release -> should scrape in 10 mins (on the same day we wait for the new release).",
    get_next_scrape_time(
        datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Releases tomorrow, last scraped after the previous release -> should scrape tomorrow at 10 AM (US/Central).
assert are_equal(
    "Releases tomorrow, last scraped after the previous release -> should scrape tomorrow at 10 AM (US/Central).",
    get_next_scrape_time(
        datetime(2023, 1, 11, 18, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 11, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
)

# Released 4 hours ago, last scraped before the previous release -> should scrape 1 min ago.
assert are_equal(
    "Releases tomorrow, last scraped before the previous release -> should scrape 1 min ago.",
    get_next_scrape_time(
        datetime(2023, 1, 11, 20, 0, tzinfo=timezone.utc),
        datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc)
    ),
    datetime(2023, 1, 11, 19, 59, tzinfo=timezone.utc)
)
