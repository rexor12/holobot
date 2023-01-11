from typing import Protocol

from holobot.sdk.queries import PaginationResult
from .models import TodoItem

class ITodoItemManager(Protocol):
    async def get_by_user(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[TodoItem]:
        ...

    async def add_todo_item(self, todo_item: TodoItem) -> None:
        ...

    async def delete_by_user(self, user_id: str, todo_item_id: int) -> None:
        ...

    async def delete_all(self, user_id: str) -> int:
        ...
