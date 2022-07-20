from .. import TodoItemManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveAllTodoItemsWorkflow(WorkflowBase):
    def __init__(self, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__()
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Removes all to-do items from your list."

    @command(
        description="Removes ALL to-do items from your list.",
        name="removeall",
        group_name="todo",
        options=(
            Option("description", "The description of the to-do item."),
        )
    )
    async def remove_all_todo_items(self, context: ServerChatInteractionContext) -> InteractionResponse:
        deleted_count = await self.__todo_item_manager.delete_all(context.author_id)
        if deleted_count > 0:
            return InteractionResponse(
                action=ReplyAction(content=f"All {deleted_count} of your to-do items have been removed.")
            )

        return InteractionResponse(
            action=ReplyAction(content="You have no to-do items to be removed.")
        )
