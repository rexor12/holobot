from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class ReminderRecord(Record):
    id: PrimaryKey[int]
    user_id: int
    server_id: int | None
    channel_id: int | None
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
