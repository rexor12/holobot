from collections.abc import Awaitable

from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
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

    def count_by_user(self, user_id: str) -> Awaitable[int]:
        return self._count_by_filter(
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

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

    def delete_by_user(self, user_id: str, todo_id: int) -> Awaitable[int]:
        return self._delete_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("user_id", Equality.EQUAL, user_id),
                ("id", Equality.EQUAL, todo_id)
            )
        )

    def delete_all_by_user(self, user_id: str) -> Awaitable[int]:
        return self._delete_by_filter(
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

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
