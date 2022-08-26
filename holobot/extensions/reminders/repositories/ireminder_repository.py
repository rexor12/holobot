from typing import Protocol

from holobot.extensions.reminders.models import Reminder
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IReminderRepository(IRepository[int, Reminder], Protocol):
    async def count_by_user(self, user_id: str) -> int:
        ...

    async def get_many(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        ...

    async def get_triggerable(self) -> tuple[Reminder, ...]:
        ...

    async def delete_by_user(self, user_id: str, reminder_id: int) -> int:
        ...
