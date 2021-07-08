from .. import TodoItemManagerInterface
from ..exceptions import InvalidTodoItemError
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveTodoItemCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__(services, "remove")
        self.__todo_item_manager: TodoItemManagerInterface = services.get(TodoItemManagerInterface)
        self.group_name = "todo"
        self.description = "Removes a to-do item from your list."
        self.options = [
            create_option("identifier", "The identifier of the to-do item.", SlashCommandOptionType.INTEGER, True)
        ]
    
    async def execute(self, context: SlashContext, identifier: int):
        try:
            await self.__todo_item_manager.delete_by_user(get_author_id(context), identifier)
            await reply(context, "The to-do item has been deleted.")
        except InvalidTodoItemError:
            await reply(context, "That to-do item doesn't exist or belong to you.")
