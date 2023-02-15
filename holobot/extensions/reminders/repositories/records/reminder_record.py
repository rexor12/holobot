from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.repositories import Record

@dataclass(kw_only=True)
class ReminderRecord(Record[int]):
    id: int
    user_id: str
    server_id: str | None
    channel_id: str | None
    message: str | None
    location: int
    created_at: datetime
    is_repeating: bool
    frequency_time: timedelta
    day_of_week: int
    until_date: datetime | None
    base_trigger: datetime
    last_trigger: datetime
    next_trigger: datetime
