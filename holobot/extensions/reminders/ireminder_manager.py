from typing import Protocol

from holobot.sdk.queries import PaginationResult
from .models import Reminder, ReminderConfig

class IReminderManager(Protocol):
    async def set_reminder(self, user_id: int, config: ReminderConfig) -> Reminder:
        ...

    async def delete_reminder(self, user_id: int, reminder_id: int) -> None:
        ...

    async def get_by_user(self, user_id: int, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        ...
