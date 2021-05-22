from .exceptions import TooManyTodoItemsError
from .models import TodoItem
from .repositories import TodoItemRepositoryInterface
from .todo_item_manager_interface import TodoItemManagerInterface
from holobot.configs import ConfiguratorInterface
from holobot.dependency_injection import injectable, ServiceCollectionInterface
from holobot.exceptions import ArgumentOutOfRangeError
from holobot.logging import LogInterface

@injectable(TodoItemManagerInterface)
class TodoItemManager(TodoItemManagerInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator = services.get(ConfiguratorInterface)
        self.__log = services.get(LogInterface)
        self.__todo_item_repository: TodoItemRepositoryInterface = services.get(TodoItemRepositoryInterface)
        self.__todo_items_per_user_max: int = self.__configurator.get("TodoLists", "TodoItemsPerUserMax", 5)
        self.__message_length_min: int = self.__configurator.get("TodoLists", "MessageLengthMin", 10)
        self.__message_length_max: int = self.__configurator.get("TodoLists", "MessageLengthMax", 192)

    async def add_todo_item(self, todo_item: TodoItem) -> None:
        if not (self.__message_length_min <= len(todo_item.message) <= self.__message_length_max):
            raise ArgumentOutOfRangeError("message", str(self.__message_length_min), str(self.__message_length_max))

        await self.__assert_todo_item_count(todo_item.user_id)
        await self.__todo_item_repository.store(todo_item)
        self.__log.debug(f"[TodoItemManager] Set new to-do item. {{ UserId = {todo_item.user_id} }}")

    async def __assert_todo_item_count(self, user_id: str) -> None:
        count = await self.__todo_item_repository.count(user_id)
        if count >= self.__todo_items_per_user_max:
            raise TooManyTodoItemsError(count)
