from .. import TodoItemManagerInterface
from ..exceptions import TooManyTodoItemsError
from ..models import TodoItem
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
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
            Option("description", "The description of the to-do item.")
        ]
    
    async def execute(self, context: ServerChatInteractionContext, description: str) -> CommandResponse:
        todo_item = TodoItem()
        todo_item.user_id = context.author_id
        todo_item.message = description
        try:
            await self.__todo_item_manager.add_todo_item(todo_item)
            return CommandResponse(
                action=ReplyAction(
                    content="The item has been added to your to-do list."
                )
            )
        except ArgumentOutOfRangeError as error:
            return CommandResponse(
                action=ReplyAction(
                    content=f"Your message's length has to be between {error.lower_bound} and {error.upper_bound}."
                )
            )
        except TooManyTodoItemsError:
            return CommandResponse(
                action=ReplyAction(
                    content="You have reached the maximum number of to-do items. Please, remove at least one to be able to add this new one."
                )
            )
        return CommandResponse()
