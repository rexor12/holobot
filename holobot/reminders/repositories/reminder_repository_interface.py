from datetime import datetime
from holobot.reminders.models.reminder import Reminder
from typing import List, Optional

class ReminderRepositoryInterface:
    async def count(self, user_id: str) -> int:
        raise NotImplementedError

    async def get(self, id: int) -> Optional[Reminder]:
        raise NotImplementedError

    async def get_triggerable(self) -> List[Reminder]:
        raise NotImplementedError

    async def store(self, reminder: Reminder) -> None:
        raise NotImplementedError
    
    async def update_next_trigger(self, reminder_id: int, next_trigger: datetime) -> None:
        raise NotImplementedError

    async def delete(self, reminder_id: int) -> None:
        raise NotImplementedError
