from typing import Optional, Protocol

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.queries import PaginationResult

class TodoItemRepositoryInterface(Protocol):
    async def count(self, user_id: str) -> int:
        ...
        
    async def get(self, todo_id: int) -> Optional[TodoItem]:
        ...
    
    async def get_many(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[TodoItem]:
        ...
    
    async def store(self, todo_item: TodoItem) -> None:
        ...

    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        ...
    
    async def delete_all(self, user_id: str) -> int:
        ...
