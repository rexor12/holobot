from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from .. import TodoItemManagerInterface
from ..exceptions import TooManyTodoItemsError
from ..models import TodoItem

@injectable(IWorkflow)
class AddTodoItemWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        todo_item_manager: TodoItemManagerInterface
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(AddTodoItemWorkflow)
        self.__todo_item_manager = todo_item_manager

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
                    content=self.__i18n_provider.get(
                        "extensions.todo_lists.add_todo_item_workflow.item_added"
                    )
                )
            )
        except ArgumentOutOfRangeError as error:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.todo_lists.add_todo_item_workflow.message_too_long_error",
                        {
                            "lower_bound": error.lower_bound,
                            "upper_bound": error.upper_bound
                        }
                    )
                )
            )
        except TooManyTodoItemsError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.todo_lists.add_todo_item_workflow.list_full_error"
                    )
                )
            )
