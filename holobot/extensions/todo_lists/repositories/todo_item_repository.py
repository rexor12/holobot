
from asyncpg.connection import Connection

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .todo_item_repository_interface import TodoItemRepositoryInterface

@injectable(TodoItemRepositoryInterface)
class TodoItemRepository(TodoItemRepositoryInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def count(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result: int | None = await connection.fetchval("SELECT COUNT(*) FROM todo_lists WHERE user_id = $1", user_id)
                return result or 0

    async def get(self, todo_id: int) -> TodoItem | None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await Query.select().columns(
                    "id", "user_id", "created_at", "message"
                ).from_table("todo_lists").where().field(
                    "id", Equality.EQUAL, todo_id
                ).compile().fetchrow(connection)
                return TodoItemRepository.__parse_todo_item(record) if record is not None else None

    async def get_many(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[TodoItem]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .select()
                    .columns("id", "user_id", "created_at", "message")
                    .from_table("todo_lists")
                    .where()
                    .field("user_id", Equality.EQUAL, user_id)
                    .paginate("id", page_index, page_size)
                    .compile()
                    .fetch(connection)
                )

                return PaginationResult(
                    result.page_index,
                    result.page_size,
                    result.total_count,
                    [TodoItemRepository.__parse_todo_item(record) for record in result.records]
                )

    async def store(self, todo_item: TodoItem) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table("todo_lists").field(
                    "user_id", todo_item.user_id
                ).field(
                    "message", todo_item.message
                ).compile().execute(connection)

    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM todo_lists WHERE user_id = $1 AND id = $2 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id, todo_id)
                return record["deleted_count"] if record is not None else 0

    async def delete_all(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM todo_lists WHERE user_id = $1 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id)
                return record["deleted_count"] if record is not None else 0

    @staticmethod
    def __parse_todo_item(record) -> TodoItem:
        todo_item = TodoItem()
        todo_item.id = record["id"]
        todo_item.user_id = record["user_id"]
        todo_item.created_at = record["created_at"]
        todo_item.message = record["message"]
        return todo_item
