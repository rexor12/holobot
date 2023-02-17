from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.reminders.models import Reminder
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IReminderRepository(IRepository[int, Reminder], Protocol):
    def count_by_user(self, user_id: str) -> Awaitable[int]:
        ...

    def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[Reminder]]:
        ...

    def get_triggerable(self) -> Awaitable[tuple[Reminder, ...]]:
        ...

    def delete_by_user(self, user_id: str, reminder_id: int) -> Awaitable[int]:
        ...
