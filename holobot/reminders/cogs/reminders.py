from datetime import datetime, timedelta, tzinfo
from typing import Optional
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown, MissingRequiredArgument
from holobot.bot import Bot
from holobot.logging.log_interface import LogInterface
from holobot.parsing.argument_parser import UNBOUND_KEY, parse_arguments
from holobot.parsing.interval_parser import parse_interval
from holobot.reminders.enums.frequency_type import FrequencyType
from holobot.reminders.exceptions.TooManyRemindersError import TooManyRemindersError
from holobot.reminders.models.reminder import Reminder
from holobot.reminders.repositories.reminder_repository_interface import ReminderRepositoryInterface

BREAK_CHARS = (" ",)
MAX_REMINDER_PER_USER = 3

class Reminders(Cog, name="Reminders"):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.__bot: Bot = bot
        self.__log: LogInterface = bot.service_collection.get(LogInterface)
        self.__reminder_repository: ReminderRepositoryInterface = bot.service_collection.get(ReminderRepositoryInterface)

    @group(aliases=["r"], brief="A group of reminder related commands.")
    async def reminders(self, context: Context):
        if not context.invoked_subcommand:
            await context.reply("You have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.user)
    @reminders.command(brief="Sets a new reminder.")
    async def set(self, context: Context, *, config: str):
        self.__log.warning(f"Setting new reminder with config '{config}'...")
        args = parse_arguments(("on", "at", "every"), config)
        if len(args[UNBOUND_KEY]) == 0:
            await context.reply("You have to specify a message for the reminder. Please, see the help for more information.")
            return
        if len(args["every"]) > 0:
            self.__log.warning("Reminder is recurring.")
            reminder = await self.__set_recurring_reminder(str(context.author.id), parse_interval(args["every"]))
        elif len(args["on"]) > 0 or len(args["at"]) > 0:
            self.__log.warning("Reminder is single occurence.")
            reminder = await self.__set_single_reminder(str(context.author.id), parse_interval(args["at"]))
        else:
            await context.reply("You have to specify either the frequency of the reminder or the date/time of the occurrence. Please, see the help for more information.")
            return
        self.__log.warning(f"Reminder: {reminder}")
        await context.reply(f"Your reminder has been set. I'll remind you at {reminder.next_trigger}.")

    async def __assert_reminder_count(self, user_id: str):
        count = await self.__reminder_repository.count(user_id)
        if count >= MAX_REMINDER_PER_USER:
            self.__log.warning("The user has too many reminders.")
            raise TooManyRemindersError(count)
    
    async def __set_recurring_reminder(self, user_id: str, frequency_time: timedelta) -> Reminder:
        await self.__assert_reminder_count(user_id)
        reminder = Reminder()
        reminder.user_id = user_id
        reminder.is_repeating = True
        reminder.frequency_type = FrequencyType.SPECIFIC
        reminder.frequency_time = frequency_time
        reminder.recalculate_next_trigger()
        await self.__reminder_repository.store(reminder)
        return reminder
    
    async def __set_single_reminder(self, user_id: str, time_at: Optional[timedelta] = None) -> Reminder:
        await self.__assert_reminder_count(user_id)
        if time_at is None:
            time_at = timedelta()

        reminder = Reminder()
        reminder.user_id = user_id
        reminder.next_trigger = self.__calculate_single_trigger(time_at)
        await self.__reminder_repository.store(reminder)
        return reminder
    
    def __calculate_single_trigger(self, time_at: timedelta) -> datetime:
        # TODO Make this aware of the user's locale. We can't expect random people to deal with UTC.
        # https://discordpy.readthedocs.io/en/stable/api.html#discord.ClientUser.locale
        current_time = datetime.utcnow()
        trigger_time = datetime(current_time.year, current_time.month, current_time.day) + time_at
        if trigger_time < current_time:
            return trigger_time + timedelta(1)
        return trigger_time
    
    @set.error
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
