from dataclasses import dataclass, field
from datetime import datetime, timedelta

from holobot.extensions.reminders.enums import DayOfWeek, ReminderLocation
from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class Reminder:
    identifier: int = -1
    user_id: str
    server_id: str | None = None
    channel_id: str | None = None
    message: str | None = None
    location: ReminderLocation = ReminderLocation.DIRECT_MESSAGE
    created_at: datetime = field(default_factory=utcnow)
    is_repeating: bool = False
    frequency_time: timedelta = field(default_factory=timedelta)
    day_of_week: int = DayOfWeek.SUNDAY
    until_date: datetime | None = None
    base_trigger: datetime = field(default_factory=utcnow)
    last_trigger: datetime = field(default_factory=utcnow)
    next_trigger: datetime = field(default_factory=utcnow)

    @property
    def is_expired(self) -> bool:
        if self.until_date is None:
            return False
        return self.next_trigger.date() > self.until_date

    def recalculate_next_trigger(self) -> None:
        if not self.is_repeating:
            raise ValueError("A non-recurring reminder cannot have a new trigger date-time.")
        current_time = utcnow()
        repeat_count = int((current_time - self.base_trigger) / self.frequency_time)
        trigger_time = self.base_trigger + (repeat_count + 1) * self.frequency_time
        if trigger_time > self.last_trigger + self.frequency_time:
            self.next_trigger = current_time
        else:
            self.next_trigger = trigger_time
