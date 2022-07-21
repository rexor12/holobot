from datetime import datetime
from typing import Optional, Protocol, Tuple

from ..models import Reminder
from holobot.sdk.queries import PaginationResult

class ReminderRepositoryInterface(Protocol):
    async def count(self, user_id: str) -> int:
        ...

    async def get(self, id: int) -> Optional[Reminder]:
        ...
    
    async def get_many(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        ...

    async def get_triggerable(self) -> Tuple[Reminder, ...]:
        ...

    async def store(self, reminder: Reminder) -> None:
        ...
    
    async def update_next_trigger(self, reminder_id: int, next_trigger: datetime) -> None:
        ...

    async def delete(self, reminder_id: int) -> None:
        ...
    
    async def delete_by_user(self, user_id: str, reminder_id: int) -> int:
        ...
