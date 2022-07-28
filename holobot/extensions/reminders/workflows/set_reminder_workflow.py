from typing import Optional

from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderConfigError, TooManyRemindersError
from ..models import ReminderConfig
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class SetReminderWorkflow(WorkflowBase):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        reminder_manager: ReminderManagerInterface
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(SetReminderWorkflow)
        self.__reminder_manager: ReminderManagerInterface = reminder_manager

    @command(
        description="Sets a new reminder.",
        name="set",
        group_name="reminder",
        options=(
            Option("message", "The message you'd like sent to you."),
            Option("in_time", "After the specified time passes. Eg. 1h30m or 01:30.", is_mandatory=False),
            Option("at_time", "At a specific moment in time. Eg. 15:30 or 15h30m.", is_mandatory=False),
            Option("every_interval", "Repeat in intervals. Eg. 1h30m, 01:30 or day/week.", is_mandatory=False)
        )
    )
    async def set_reminder(
        self,
        context: ServerChatInteractionContext,
        message: str,
        in_time: Optional[str] = None,
        at_time: Optional[str] = None,
        every_interval: Optional[str] = None
    ) -> InteractionResponse:
        reminder_config = ReminderConfig()
        if in_time is not None and len(in_time) > 0:
            reminder_config.in_time = parse_interval(in_time)
        if at_time is not None and len(at_time) > 0:
            reminder_config.at_time = parse_interval(at_time)
        if every_interval is not None and len(every_interval) > 0:
            reminder_config.every_interval = parse_interval(every_interval)
        reminder_config.message = message

        try:
            reminder = await self.__reminder_manager.set_reminder(context.author_id, reminder_config)
            self.__logger.debug("Set new reminder", user_id=context.author_id, reminder_id=reminder.id)
            return InteractionResponse(
                action=ReplyAction(content=f"I'll remind you at {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC.")
            )
        except ArgumentError as error:
            if error.argument_name == "message":
                return InteractionResponse(
                    action=ReplyAction(content="Your message is either too short or too long. Please, see the help for more information.")
                )
            elif error.argument_name == "occurrence":
                return InteractionResponse(
                    action=ReplyAction(content="You have to specify either the frequency of the reminder or the date/time of the occurrence. Please, see the help for more information.")
                )
            else: raise
        except InvalidReminderConfigError as error:
            return InteractionResponse(
                action=ReplyAction(content=f"The parameters '{error.param1}' and '{error.param2}' cannot be used together.")
            )
        except TooManyRemindersError:
            return InteractionResponse(
                action=ReplyAction(content="You have reached the maximum number of reminders. Please, remove at least one to be able to add this new one.")
            )
