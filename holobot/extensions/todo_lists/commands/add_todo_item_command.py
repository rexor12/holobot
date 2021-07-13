from .. import TodoItemManagerInterface
from ..exceptions import TooManyTodoItemsError
from ..models import TodoItem
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(CommandInterface)
class AddTodoItemCommand(CommandBase):
    def __init__(self, log: LogInterface, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("add")
        self.__log: LogInterface = log.with_name("TodoLists", "AddTodoItemCommand")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Adds a new item to your to-do list."
        self.options = [
            create_option("description", "The description of the to-do item.", SlashCommandOptionType.STRING, True)
        ]
    
    async def execute(self, context: SlashContext, description: str):
        todo_item = TodoItem()
        todo_item.user_id = get_author_id(context)
        todo_item.message = description
        try:
            await self.__todo_item_manager.add_todo_item(todo_item)
            await reply(context, "The item has been added to your to-do list.")
        except ArgumentOutOfRangeError as error:
            await reply(context, f"Your message's length has to be between {error.lower_bound} and {error.upper_bound}.")
        except TooManyTodoItemsError:
            await reply(context, "You have reached the maximum number of to-do items. Please, remove at least one to be able to add this new one.")
