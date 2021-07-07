from .. import TodoItemManagerInterface
from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllTodoItemsCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__(services, "removeall")
        self.__todo_item_manager: TodoItemManagerInterface = services.get(TodoItemManagerInterface)
        self.group_name = "todo"
        self.description = "Removes all to-do items from your list."
    
    async def execute(self, context: SlashContext):
        deleted_count = await self.__todo_item_manager.delete_all(get_author_id(context))
        if deleted_count > 0:
            await reply(context, f"All {deleted_count} of your to-do items have been removed.")
        else: await reply(context, "You have no to-do items to be removed.")
