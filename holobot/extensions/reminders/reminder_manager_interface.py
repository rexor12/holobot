from .models import Reminder, ReminderConfig
from typing import Tuple

class ReminderManagerInterface:
    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        raise NotImplementedError
    
    async def delete_reminder(self, user_id: str, reminder_id: int) -> None:
        raise NotImplementedError

    async def get_by_user(self, user_id: str, offset: int, page_size: int) -> Tuple[Reminder, ...]:
        raise NotImplementedError
