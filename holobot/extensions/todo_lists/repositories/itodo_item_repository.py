from typing import Protocol

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ITodoItemRepository(IRepository[int, TodoItem], Protocol):
    async def count_by_user(self, user_id: str) -> int:
        ...

    async def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[TodoItem]:
        ...

    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        ...

    async def delete_all_by_user(self, user_id: str) -> int:
        ...
