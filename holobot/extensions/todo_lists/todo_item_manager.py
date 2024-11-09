from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.queries import PaginationResult
from .exceptions import InvalidTodoItemError, TooManyTodoItemsError
from .itodo_item_manager import ITodoItemManager
from .models import TodoItem, TodoOptions
from .repositories import ITodoItemRepository

@injectable(ITodoItemManager)
class TodoItemManager(ITodoItemManager):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        options: IOptions[TodoOptions],
        todo_item_repository: ITodoItemRepository
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(TodoItemManager)
        self.__todo_item_repository = todo_item_repository
        self.__options = options

    async def get_by_user(self, user_id: int, page_index: int, page_size: int) -> PaginationResult[TodoItem]:
        return await self.__todo_item_repository.get_many(user_id, page_index, page_size)

    async def add_todo_item(self, todo_item: TodoItem) -> None:
        options = self.__options.value
        if not (options.MessageLengthMin <= len(todo_item.message) <= options.MessageLengthMax):
            raise ArgumentOutOfRangeError(
                "message",
                str(options.MessageLengthMin),
                str(options.MessageLengthMax)
            )

        await self.__assert_todo_item_count(todo_item.user_id)
        todo_item.identifier = await self.__todo_item_repository.add(todo_item)
        self.__logger.debug("Set new to-do item", user_id=todo_item.user_id)

    async def delete_by_user(self, user_id: int, todo_item_id: int) -> None:
        if not user_id:
            raise ValueError("The user identifier cannot be none.")

        deleted_count = await self.__todo_item_repository.delete_by_user(user_id, todo_item_id)
        if deleted_count == 0:
            raise InvalidTodoItemError("The specified to-do item doesn't exist or belong to the specified user.")

    async def delete_all(self, user_id: int) -> int:
        if not user_id:
            raise ValueError("The user identifier cannot be none.")

        return await self.__todo_item_repository.delete_all_by_user(user_id)

    async def __assert_todo_item_count(self, user_id: int) -> None:
        count = await self.__todo_item_repository.count_by_user(user_id)
        if count >= self.__options.value.TodoItemsPerUserMax:
            raise TooManyTodoItemsError(count)
