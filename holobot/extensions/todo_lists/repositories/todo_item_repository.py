from .todo_item_repository_interface import TodoItemRepositoryInterface
from ..models import TodoItem
from asyncpg.connection import Connection
from holobot.database import DatabaseManagerInterface
from holobot.dependency_injection import injectable, ServiceCollectionInterface
from typing import List, Optional

@injectable(TodoItemRepositoryInterface)
class TodoItemRepository(TodoItemRepositoryInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = service_collection.get(DatabaseManagerInterface)
        
    async def count(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result: Optional[int] = await connection.fetchval("SELECT COUNT(*) FROM todo_lists WHERE user_id = $1", user_id)
                return result or 0

    async def get(self, todo_id: int) -> Optional[TodoItem]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "SELECT id, user_id, created_at, message FROM todo_lists WHERE id = $1"
                ), todo_id)
                return TodoItemRepository.__parse_todo_item(record) if record is not None else None
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> List[TodoItem]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch((
                    "SELECT id, user_id, created_at, message FROM todo_lists WHERE user_id = $1 LIMIT $3 OFFSET $2"
                ), user_id, start_offset, page_size)
                return [TodoItemRepository.__parse_todo_item(record) for record in records]
    
    async def store(self, todo_item: TodoItem) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await connection.execute((
                    "INSERT INTO todo_lists (user_id, message)"
                    " VALUES ($1, $2)"
                ), todo_item.user_id, todo_item.message)
    
    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM todo_lists WHERE user_id = $1 AND id = $2 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id, todo_id)
                return record["deleted_count"]
    
    async def delete_all(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM todo_lists WHERE user_id = $1 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id)
                return record["deleted_count"]
    
    @staticmethod
    def __parse_todo_item(record) -> TodoItem:
        todo_item = TodoItem()
        todo_item.id = record["id"]
        todo_item.user_id = record["user_id"]
        todo_item.created_at = record["created_at"]
        todo_item.message = record["message"]
        return todo_item
