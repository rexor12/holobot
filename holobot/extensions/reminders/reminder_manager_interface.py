from .models import Reminder, ReminderConfig

class ReminderManagerInterface:
    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        raise NotImplementedError
