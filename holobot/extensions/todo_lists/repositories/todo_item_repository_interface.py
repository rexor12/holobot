from ..models import TodoItem
from typing import Optional, Tuple

class TodoItemRepositoryInterface:
    async def count(self, user_id: str) -> int:
        raise NotImplementedError
        
    async def get(self, todo_id: int) -> Optional[TodoItem]:
        raise NotImplementedError
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> Tuple[TodoItem, ...]:
        raise NotImplementedError
    
    async def store(self, todo_item: TodoItem) -> None:
        raise NotImplementedError

    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        raise NotImplementedError
    
    async def delete_all(self, user_id: str) -> int:
        raise NotImplementedError
