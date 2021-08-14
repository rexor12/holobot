from .. import TodoItemManagerInterface
from discord.embeds import Embed
from discord.ext.commands.context import Context
from discord_slash.context import SlashContext
from holobot.discord.components import DynamicPager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_author_id
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

@injectable(CommandInterface)
class ViewTodoItemsCommand(CommandBase):
    def __init__(self, log: LogInterface, messaging: IMessaging, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__("view")
        self.__log: LogInterface = log.with_name("TodoLists", "ViewTodoItemsCommand")
        self.__messaging: IMessaging = messaging
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager
        self.group_name = "todo"
        self.description = "Displays all your to-do items."
    
    async def execute(self, context: SlashContext) -> CommandResponse:
        await DynamicPager(self.__messaging, self.__log, context, self.__create_todo_list_embed)
        return CommandResponse()

    async def __create_todo_list_embed(self, context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        items = await self.__todo_item_manager.get_by_user(get_author_id(context), start_offset, page_size)
        if len(items) == 0:
            return None
        
        embed = Embed(
            title="To-do list",
            description=f"To-do items of {context.author.mention}.",
            color=0xeb7d00
        ).set_footer(text="Use the to-do item's number for removal.")
        for item in items:
            embed.add_field(
                name=f"#{item.id}",
                value=item.message,
                inline=False
            )
        return embed
