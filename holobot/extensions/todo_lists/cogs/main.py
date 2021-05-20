from .. import TodoItemManagerInterface
from ..exceptions import TooManyTodoItemsError
from ..models import TodoItem
from ..repositories import TodoItemRepositoryInterface
from discord.embeds import Embed
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown, MissingRequiredArgument
from holobot import Bot
from holobot.display import DynamicPager
from holobot.exceptions import ArgumentOutOfRangeError
from holobot.logging import LogInterface
from typing import Optional

class TodoLists(Cog, name="To-do list"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot: Bot = bot
        self.__log: LogInterface = bot.service_collection.get(LogInterface)
        self.__todo_item_manager: TodoItemManagerInterface = bot.service_collection.get(TodoItemManagerInterface)
        self.__todo_item_repository: TodoItemRepositoryInterface = bot.service_collection.get(TodoItemRepositoryInterface)
    
    @group(aliases=["td"], brief="A group of reminder related commands.")
    async def todos(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.user)
    @todos.command(aliases=["a"], brief="Adds a new item to your to-do list.", description="Adds a new item to your to-do list.")
    async def add(self, context: Context, *, message: str):
        todo_item = TodoItem()
        todo_item.user_id = str(context.author.id)
        todo_item.message = message
        await self.__todo_item_manager.add_todo_item(todo_item)
        await context.reply(f"The item has been added to your to-do list.")

    @cooldown(1, 10, BucketType.user)
    @todos.command(name="viewall", aliases=["va"], brief="Displays all your to-do items.", description="Displays all of your to-do items in a paging box you can navigate with reactions.")
    async def view_all(self, context: Context):
        await DynamicPager(self.__bot, context, self.__create_todo_list_embed)
    
    @cooldown(1, 10, BucketType.user)
    @todos.command(aliases=["r"], brief="Removes the to-do item with the specified identifier.", description="To find the identifier of your to-do item, view your to-do list and use the numbers for removal.")
    async def remove(self, context: Context, reminder_id: int):
        deleted_count = await self.__todo_item_repository.delete_by_user(str(context.author.id), reminder_id)
        if deleted_count == 0:
            await context.reply("That to-do item doesn't exist or belong to you.")
            return
        await context.reply("The to-do item has been deleted.")

    async def __create_todo_list_embed(self, context: Context, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        items = await self.__todo_item_repository.get_many(str(context.author.id), start_offset, page_size)
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
    
    @add.error
    @view_all.error
    @remove.error
    async def __on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.reply(f"You're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        if isinstance(error, MissingRequiredArgument):
            await context.reply("You used an invalid syntax for this command. Please, see the help for more information.")
            return
        if isinstance(error, CommandInvokeError) and isinstance(error.original, TooManyTodoItemsError):
            await context.reply("You have reached the maximum number of to-do items. Please, remove at least one to be able to add this new one.")
            return
        if isinstance(error, CommandInvokeError) and isinstance(error.original, ArgumentOutOfRangeError):
            await context.reply(f"Your message's length has to be between {error.original.lower_bound} and {error.original.upper_bound}.")
            return
        await context.reply("An internal error has occurred. Please, try again later.")
        self.__log.error(f"[Cogs] [TodoLists] Failed to process the command '{context.command}'.", error)
    
def setup(bot: Bot):
    bot.add_cog(TodoLists(bot))
