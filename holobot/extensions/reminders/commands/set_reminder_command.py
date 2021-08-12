from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderConfigError, TooManyRemindersError
from ..models import ReminderConfig
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class SetReminderCommand(CommandBase):
    def __init__(self, log: LogInterface, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__("set")
        self.__log: LogInterface = log.with_name("Reminders", "SetReminderCommand")
        self.__reminder_manager: ReminderManagerInterface = reminder_manager
        self.group_name = "reminder"
        self.description = "Sets a new reminder."
        self.options = [
            create_option("message", "The message you'd like sent to you.", SlashCommandOptionType.STRING, True),
            create_option("in_time", "After the specified time passes. Eg. 1h30m or 01:30.", SlashCommandOptionType.STRING, False),
            create_option("at_time", "At a specific moment in time. Eg. 15:30 or 15h30m.", SlashCommandOptionType.STRING, False),
            create_option("every_interval", "Repeat in intervals. Eg. 1h30m, 01:30 or day/week.", SlashCommandOptionType.STRING, False)
        ]

    async def execute(self, context: SlashContext, message: str, in_time: Optional[str] = None, at_time: Optional[str] = None, every_interval: Optional[str] = None) -> None:
        reminder_config = ReminderConfig()
        if in_time is not None and len(in_time) > 0:
            reminder_config.in_time = parse_interval(in_time)
        if at_time is not None and len(at_time) > 0:
            reminder_config.at_time = parse_interval(at_time)
        if every_interval is not None and len(every_interval) > 0:
            reminder_config.every_interval = parse_interval(every_interval)
        reminder_config.message = message

        try:
            user_id = get_author_id(context)
            reminder = await self.__reminder_manager.set_reminder(user_id, reminder_config)
            await reply(context, f"I'll remind you at {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC.")
            self.__log.debug(f"Set new reminder. {{ UserId = {user_id}, ReminderId = {reminder.id} }}")
        except ArgumentError as error:
            if error.argument_name == "message":
                await reply(context, "Your message is either too short or too long. Please, see the help for more information.")
            elif error.argument_name == "occurrence":
                await reply(context, "You have to specify either the frequency of the reminder or the date/time of the occurrence. Please, see the help for more information.")
            else: raise
        except InvalidReminderConfigError as error:
            await reply(context, f"The parameters '{error.param1}' and '{error.param2}' cannot be used together.")
        except TooManyRemindersError:
            await reply(context, "You have reached the maximum number of reminders. Please, remove at least one to be able to add this new one.")
