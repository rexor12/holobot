from holobot.reminders.models.reminder import Reminder
from holobot.reminders.models.reminder_config import ReminderConfig

class ReminderManagerInterface:
    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        raise NotImplementedError