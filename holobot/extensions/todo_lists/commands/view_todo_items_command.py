from .. import TodoItemManagerInterface
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class ViewTodoItemsCommand(CommandBase):
    def __init__(self, log: LogInterface, messaging: IMessaging, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("view")
        self.__log: LogInterface = log.with_name("TodoLists", "ViewTodoItemsCommand")
        self.__messaging: IMessaging = messaging
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Displays all your to-do items."
    
    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await Pager(self.__messaging, self.__log, context, self.__create_todo_list_embed)
        return CommandResponse()

    async def __create_todo_list_embed(self, context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        items = await self.__todo_item_manager.get_by_user(context.author_id, start_offset, page_size)
        if len(items) == 0:
            return None
        
        embed = Embed(
            title="To-do list",
            description=f"To-do items of <@{context.author_id}>.",
            fields=[
                EmbedField(f"#{item.id}", item.message, False) for item in items
            ],
            footer=EmbedFooter("Use the to-do item's number for removal.")
        )

        return embed
