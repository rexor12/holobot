from .models import TodoItem
from typing import Tuple

class TodoItemManagerInterface:
    async def get_by_user(self, user_id: str, offset: int, page_size: int) -> Tuple[TodoItem, ...]:
        raise NotImplementedError

    async def add_todo_item(self, todo_item: TodoItem) -> None:
        raise NotImplementedError
    
    async def delete_by_user(self, user_id: str, todo_item_id: int) -> None:
        raise NotImplementedError
    
    async def delete_all(self, user_id: str) -> int:
        raise NotImplementedError
