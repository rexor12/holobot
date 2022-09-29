from dataclasses import dataclass
from datetime import timedelta

@dataclass(kw_only=True)
class ReminderConfig:
    in_time: timedelta | None = None
    at_time: timedelta | None = None
    every_interval: timedelta | None = None
    message: str | None = None
