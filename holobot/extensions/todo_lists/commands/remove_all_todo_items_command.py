from .. import TodoItemManagerInterface
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllTodoItemsCommand(CommandBase):
    def __init__(self, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("removeall")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Removes all to-do items from your list."
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        deleted_count = await self.__todo_item_manager.delete_all(get_author_id(context))
        if deleted_count > 0:
            await reply(context, f"All {deleted_count} of your to-do items have been removed.")
        else: await reply(context, "You have no to-do items to be removed.")
        return CommandResponse()
