from .. import TodoItemManagerInterface
from ..exceptions import InvalidTodoItemError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveTodoItemWorkflow(WorkflowBase):
    def __init__(self, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__()
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
    
    @command(
        description="Removes a to-do item from your list.",
        name="remove",
        group_name="todo",
        options=(
            Option("identifier", "The identifier of the to-do item.", OptionType.INTEGER),
        )
    )
    async def remove_todo_item(
        self,
        context: ServerChatInteractionContext,
        identifier: int
    ) -> InteractionResponse:
        try:
            await self.__todo_item_manager.delete_by_user(context.author_id, identifier)
            return InteractionResponse(
                action=ReplyAction(
                    content="The to-do item has been deleted."
                )
            )
        except InvalidTodoItemError:
            return InteractionResponse(
                action=ReplyAction(
                    content="That to-do item doesn't exist or belong to you."
                )
            )
