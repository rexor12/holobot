from .. import ReminderManagerInterface
from ..exceptions import ArgumentError, TooManyRemindersError
from ..models import ReminderConfig
from ..repositories import ReminderRepositoryInterface
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command, cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown, MissingRequiredArgument
from holobot.bot import Bot
from holobot.display.dynamic_pager import DynamicPager
from holobot.logging.log_interface import LogInterface
from holobot.parsing.argument_parser import UNBOUND_KEY, parse_arguments
from holobot.parsing.interval_parser import parse_interval
from typing import Optional

SET_DESCRIPTION = (
    "Examples:\n"
    "- Set a reminder that is triggered after a specific time:\n"
    "h!reminders set in 3h15m Drink some water.\n\n"
    "- Set a reminder that is triggered at a specific absolute time:\n"
    "h!reminders set at 16:32 Eat a bit of food.\n"
    "This will be triggered when the clock hits 16:32 _in the UTC time zone_. If it's already past 16:32, the reminder will be triggered tomorrow.\n\n"
    "- Set a reminder that repeats after a specific time until removed:\n"
    "h!reminders set every 30m Move your body.\n"
    "h!reminders set every day Don't forget to wake up."
)

class Reminders(Cog, name="Reminders"):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.__bot: Bot = bot
        self.__log: LogInterface = bot.service_collection.get(LogInterface)
        self.__reminder_manager: ReminderManagerInterface = bot.service_collection.get(ReminderManagerInterface)
        self.__reminder_repository: ReminderRepositoryInterface = bot.service_collection.get(ReminderRepositoryInterface)

    @group(aliases=["r"], brief="A group of reminder related commands.")
    async def reminders(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.user)
    @reminders.command(aliases=["s"], brief="Sets a new reminder.", description=SET_DESCRIPTION)
    async def set(self, context: Context, *, config: str):
        await self.__set_reminder(context, config)

    @command(brief="Shorthand for <h!reminders set>.", description="See the help for the mirrored command.")
    async def remindme(self, context: Context, *, config: str):
        await self.__set_reminder(context, config)

    @cooldown(1, 10, BucketType.user)
    @reminders.command(name="viewall", aliases=["va"], brief="Displays all your reminders.", description="Displays all of your reminders in a paging box you can navigate with reactions.")
    async def view_all(self, context: Context):
        await DynamicPager(self.__bot, context, self.__create_reminder_embed)
    
    @cooldown(1, 10, BucketType.user)
    @reminders.command(aliases=["r"], brief="Removes the reminder with the specified identifier.", description="To find the identifier of your reminder, view your reminders and use the numbers for removal.")
    async def remove(self, context: Context, reminder_id: int):
        deleted_count = await self.__reminder_repository.delete_by_user(str(context.author.id), reminder_id)
        if deleted_count == 0:
            await context.reply("That reminder doesn't exist or belong to you.")
            return
        await context.reply("The reminder has been deleted.")

    async def __set_reminder(self, context: Context, config: str) -> None:
        args = parse_arguments(("at", "every", "in"), config)
        reminder_config = ReminderConfig()
        if len(args["at"]) > 0:
            reminder_config.at_time = parse_interval(args["at"])
        if len(args["in"]) > 0:
            reminder_config.in_time = parse_interval(args["in"])
        if len(args["every"]) > 0:
            reminder_config.every_interval = parse_interval(args["every"])
        reminder_config.message = args[UNBOUND_KEY]
        try:
            reminder = await self.__reminder_manager.set_reminder(str(context.author.id), reminder_config)
            await context.reply(f"Your reminder has been set. I'll remind you at {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC.")
        except ArgumentError as error:
            if error.argument_name == "message":
                await context.reply("Your message is either too short or too long. Please, see the help for more information.")
            elif error.argument_name == "occurrence":
                await context.reply("You have to specify either the frequency of the reminder or the date/time of the occurrence. Please, see the help for more information.")
            else: raise
        except TooManyRemindersError:
            await context.reply("You have reached the maximum number of reminders. Please, remove at least one to be able to add this new one.")

    async def __create_reminder_embed(self, context: Context, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        reminders = await self.__reminder_repository.get_many(str(context.author.id), start_offset, page_size)
        if len(reminders) == 0:
            return None
        
        embed = Embed(
            title="Reminders",
            description=f"Reminders of {context.author.mention}.",
            color=0xeb7d00
        ).set_footer(text="Use the reminder's number for removal.")
        for reminder in reminders:
            embed.add_field(
                name=f"#{reminder.id}",
                value=(
                    f"> Message: {reminder.message}\n"
                    f"> Next trigger: {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC\n"
                    f"> Repeats: {'yes' if reminder.is_repeating else 'no'}"
                ),
                inline=False
            )
        return embed

    @set.error
    @view_all.error
    @remove.error
    async def __on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.reply(f"You're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        if isinstance(error, MissingRequiredArgument):
            await context.reply("You used an invalid syntax for this command. Please, see the help for more information.")
            return
        if isinstance(error, CommandInvokeError) and isinstance(error.original, TooManyRemindersError):
            await context.reply("You have reached the maximum number of reminders. Please, remove at least one to be able to add this new one.")
            return
        await context.reply("An internal error has occurred. Please, try again later.")
        self.__log.error(f"[Cogs] [Reminders] Failed to process the command '{context.command}'.", error)

def setup(bot: Bot):
    bot.add_cog(Reminders(bot))
