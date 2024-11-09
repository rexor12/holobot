from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class ITodoItemRepository(IRepository[int, TodoItem], Protocol):
    def count_by_user(self, user_id: int) -> Awaitable[int]:
        ...

    def get_many(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[TodoItem]]:
        ...

    def delete_by_user(self, user_id: int, todo_id: int) -> Awaitable[int]:
        ...

    def delete_all_by_user(self, user_id: int) -> Awaitable[int]:
        ...
