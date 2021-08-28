from .. import TodoItemManagerInterface
from ..exceptions import InvalidTodoItemError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveTodoItemCommand(CommandBase):
    def __init__(self, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("remove")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Removes a to-do item from your list."
        self.options = [
            Option("identifier", "The identifier of the to-do item.", OptionType.INTEGER)
        ]
    
    async def execute(self, context: ServerChatInteractionContext, identifier: int) -> CommandResponse:
        try:
            await self.__todo_item_manager.delete_by_user(context.author_id, identifier)
            return CommandResponse(
                action=ReplyAction(
                    content="The to-do item has been deleted."
                )
            )
        except InvalidTodoItemError:
            return CommandResponse(
                action=ReplyAction(
                    content="That to-do item doesn't exist or belong to you."
                )
            )

        return CommandResponse()
