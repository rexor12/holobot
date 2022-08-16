from typing import Protocol

from holobot.sdk.queries import PaginationResult
from .models import Reminder, ReminderConfig

class ReminderManagerInterface(Protocol):
    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        ...
    
    async def delete_reminder(self, user_id: str, reminder_id: int) -> None:
        ...

    async def get_by_user(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        ...
