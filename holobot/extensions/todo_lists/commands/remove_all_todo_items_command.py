from .. import TodoItemManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllTodoItemsCommand(CommandBase):
    def __init__(self, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("removeall")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Removes all to-do items from your list."
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        deleted_count = await self.__todo_item_manager.delete_all(context.author_id)
        if deleted_count > 0:
            return CommandResponse(
                action=ReplyAction(content=f"All {deleted_count} of your to-do items have been removed.")
            )

        return CommandResponse(
            action=ReplyAction(content="You have no to-do items to be removed.")
        )
