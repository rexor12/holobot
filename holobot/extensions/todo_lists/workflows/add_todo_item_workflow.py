from .. import TodoItemManagerInterface
from ..exceptions import TooManyTodoItemsError
from ..models import TodoItem
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IWorkflow)
class AddTodoItemWorkflow(WorkflowBase):
    def __init__(self, log: LogInterface, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("TodoLists", "AddTodoItemWorkflow")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager

    @command(
        description="Adds a new item to your to-do list.",
        name="add",
        group_name="todo",
        options=(
            Option("description", "The description of the to-do item."),
        )
    )
    async def add_todo_item(
        self,
        context: ServerChatInteractionContext,
        description: str
    ) -> InteractionResponse:
        todo_item = TodoItem()
        todo_item.user_id = context.author_id
        todo_item.message = description
        try:
            await self.__todo_item_manager.add_todo_item(todo_item)
            return InteractionResponse(
                action=ReplyAction(
                    content="The item has been added to your to-do list."
                )
            )
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(
                    content=f"Your message's length has to be between {error.lower_bound} and {error.upper_bound}."
                )
            )
        except TooManyTodoItemsError:
            return InteractionResponse(
                action=ReplyAction(
                    content="You have reached the maximum number of to-do items. Please, remove at least one to be able to add this new one."
                )
            )
