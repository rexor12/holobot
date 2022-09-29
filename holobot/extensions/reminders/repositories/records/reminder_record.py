from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class ReminderRecord(Entity[int]):
    id: int
    user_id: str
    message: str | None
    created_at: datetime
    is_repeating: bool
    frequency_time: timedelta
    day_of_week: int
    until_date: datetime | None
    base_trigger: datetime
    last_trigger: datetime
    next_trigger: datetime
