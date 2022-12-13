from dataclasses import dataclass
from datetime import timedelta

from holobot.extensions.reminders.enums import ReminderLocation

@dataclass(kw_only=True)
class ReminderConfig:
    server_id: str | None = None
    channel_id: str | None = None
    in_time: timedelta | None = None
    at_time: timedelta | None = None
    every_interval: timedelta | None = None
    message: str | None = None
    location: ReminderLocation = ReminderLocation.DIRECT_MESSAGE
