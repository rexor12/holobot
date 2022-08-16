from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from .. import TodoItemManagerInterface

@injectable(IWorkflow)
class RemoveAllTodoItemsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        todo_item_manager: TodoItemManagerInterface
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__todo_item_manager = todo_item_manager

    @command(
        description="Removes ALL to-do items from your list.",
        name="removeall",
        group_name="todo"
    )
    async def remove_all_todo_items(self, context: ServerChatInteractionContext) -> InteractionResponse:
        deleted_count = await self.__todo_item_manager.delete_all(context.author_id)
        if deleted_count > 0:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.todo_lists.remove_all_todo_items_workflow.items_deleted",
                    { "count": deleted_count }
                ))
            )

        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                "extensions.todo_lists.remove_all_todo_items_workflow.no_todo_items_error"
            ))
        )
