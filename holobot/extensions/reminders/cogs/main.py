from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderError, TooManyRemindersError
from ..models import ReminderConfig
from ..parsing import UNBOUND_KEY, parse_arguments, parse_interval
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import command, cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown, MissingRequiredArgument
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.bot import Bot
from holobot.discord.components import DynamicPager
from holobot.sdk.exceptions import ArgumentError
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

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

    @group(aliases=["r"], brief="A group of reminder related commands.")
    async def reminders(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.user)
    @reminders.command(aliases=["s"], brief="Sets a new reminder.", description=SET_DESCRIPTION)
    async def set(self, context: Context, *, config: str):
        args = parse_arguments(("at", "every", "in"), config)
        await self.__set_reminder(context, args[UNBOUND_KEY], args["in"], args["at"], args["every"])

    @cog_ext.cog_subcommand(base="reminder", name="set", description="Sets a new reminder.", guild_ids=[822228166381797427], options=[
        create_option("message", "The message you'd like sent to you.", SlashCommandOptionType.STRING, True),
        create_option("in_time", "After the specified time passes. Eg. 1h30m or 01:30.", SlashCommandOptionType.STRING, False),
        create_option("at_time", "At a specific moment in time. Eg. 15:30 or 15h30m.", SlashCommandOptionType.STRING, False),
        create_option("every_interval", "Repeat in intervals. Eg. 1h30m, 01:30 or day/week.", SlashCommandOptionType.STRING, False)
    ])
    async def slash_set(self, context: SlashContext, message: str, in_time: Optional[str] = None, at_time: Optional[str] = None, every_interval: Optional[str] = None):
        await self.__set_reminder(context, message, in_time, at_time, every_interval)

    @cooldown(1, 10, BucketType.user)
    @command(brief="Shorthand for <h!reminders set>.", description="See the help for the mirrored command.")
    async def remindme(self, context: Context, *, config: str):
        args = parse_arguments(("at", "every", "in"), config)
        await self.__set_reminder(context, args[UNBOUND_KEY], args["in"], args["at"], args["every"])

    @cooldown(1, 10, BucketType.user)
    @reminders.command(name="viewall", aliases=["va"], brief="Displays all your reminders.", description="Displays all of your reminders in a paging box you can navigate with reactions.")
    async def view_all(self, context: Context):
        await DynamicPager(self.__bot, context, self.__create_reminder_embed)
    
    @cooldown(1, 10, BucketType.user)
    @reminders.command(aliases=["r"], brief="Removes the reminder with the specified identifier.", description="To find the identifier of your reminder, view your reminders and use the numbers for removal.")
    async def remove(self, context: Context, reminder_id: int):
        await self.__delete_reminder(context, reminder_id)
    
    @cog_ext.cog_subcommand(base="reminder", name="remove", description="Removes a reminder.", guild_ids=[822228166381797427], options=[
        create_option("id", "The identifier of the reminder.", SlashCommandOptionType.INTEGER, True)
    ])
    async def slash_remove(self, context: SlashContext, id: int):
        await self.__delete_reminder(context, id)

    async def __set_reminder(self, context: Union[Context, SlashContext],
        message: str, in_time: Optional[str], at_time: Optional[str],
        every_interval: Optional[str]) -> None:
        reminder_config = ReminderConfig()
        if in_time is not None and len(in_time) > 0:
            reminder_config.in_time = parse_interval(in_time)
        if at_time is not None and len(at_time) > 0:
            reminder_config.at_time = parse_interval(at_time)
        if every_interval is not None and len(every_interval) > 0:
            reminder_config.every_interval = parse_interval(every_interval)
        reminder_config.message = message

        try:
            reminder = await self.__reminder_manager.set_reminder(get_author_id(context), reminder_config)
            await reply(context, f"I'll remind you at {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC.")
        except ArgumentError as error:
            if error.argument_name == "message":
                await reply(context, "Your message is either too short or too long. Please, see the help for more information.")
            elif error.argument_name == "occurrence":
                await reply(context, "You have to specify either the frequency of the reminder or the date/time of the occurrence. Please, see the help for more information.")
            else: raise
        except TooManyRemindersError:
            await reply(context, "You have reached the maximum number of reminders. Please, remove at least one to be able to add this new one.")

    async def __delete_reminder(self, context: Union[Context, SlashContext], reminder_id: int) -> None:
        try:
            await self.__reminder_manager.delete_reminder(get_author_id(context), reminder_id)
            await reply(context, "The reminder has been deleted.")
        except InvalidReminderError:
            await reply(context, "That reminder doesn't exist or belong to you.")

    async def __create_reminder_embed(self, context: Context, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        reminders = await self.__reminder_manager.get_by_user(get_author_id(context), start_offset, page_size)
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
