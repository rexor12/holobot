from .models import TodoItem

class TodoItemManagerInterface:
    async def add_todo_item(self, todo_item: TodoItem) -> None:
        raise NotImplementedError
