
from typing import cast

from asyncpg.connection import Connection

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.exceptions import DatabaseError
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .itodo_item_repository import ITodoItemRepository
from .records import TodoItemRecord

@injectable(ITodoItemRepository)
class TodoItemRepository(
    RepositoryBase[int, TodoItemRecord, TodoItem],
    ITodoItemRepository
):
    @property
    def record_type(self) -> type[TodoItemRecord]:
        return TodoItemRecord

    @property
    def model_type(self) -> type[TodoItem]:
        return TodoItem

    @property
    def table_name(self) -> str:
        return "todo_lists"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def count_by_user(self, user_id: str) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .select()
                    .column("COUNT(*)")
                    .from_table(self.table_name)
                    .where()
                    .field("user_id", Equality.EQUAL, user_id)
                    .compile()
                    .fetchval(connection)
                )

                return result or 0

    async def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[TodoItem]:
        return await self._paginate(
            "id",
            page_index,
            page_size,
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

    async def delete_by_user(self, user_id: str, todo_id: int) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .delete()
                    .from_table(self.table_name)
                    .where()
                    .fields(
                        Connector.AND,
                        ("user_id", Equality.EQUAL, user_id),
                        ("id", Equality.EQUAL, todo_id)
                    )
                    .compile()
                    .execute(connection)
                )

                if not isinstance(result, CommandComplete):
                    raise DatabaseError("Failed to delete some records.")

                return cast(CommandComplete[DeleteCommandTag], result).command_tag.rows

    async def delete_all_by_user(self, user_id: str) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .delete()
                    .from_table(self.table_name)
                    .where()
                    .field("user_id", Equality.EQUAL, user_id)
                    .compile()
                    .execute(connection)
                )

                if not isinstance(result, CommandComplete):
                    raise DatabaseError("Failed to delete some records.")

                return cast(CommandComplete[DeleteCommandTag], result).command_tag.rows

    def _map_record_to_model(self, record: TodoItemRecord) -> TodoItem:
        return TodoItem(
            identifier=record.id,
            user_id=record.user_id,
            created_at=record.created_at,
            message=record.message
        )

    def _map_model_to_record(self, model: TodoItem) -> TodoItemRecord:
        return TodoItemRecord(
            id=model.identifier,
            user_id=model.user_id,
            created_at=model.created_at,
            message=model.message
        )
