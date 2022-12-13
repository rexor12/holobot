from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.reminders import ReminderManagerInterface
from holobot.extensions.reminders.enums import ReminderLocation
from holobot.extensions.reminders.exceptions import (
    InvalidReminderConfigError, TooManyRemindersError
)
from holobot.extensions.reminders.models import ReminderConfig
from holobot.sdk.chrono import InvalidInputError, parse_interval
from holobot.sdk.exceptions import ArgumentError, ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class SetReminderWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reminder_manager: ReminderManagerInterface
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(SetReminderWorkflow)
        self.__reminder_manager = reminder_manager

    @command(
        description="Sets a new reminder.",
        name="set",
        group_name="reminder",
        options=(
            Option("message", "The message you'd like sent to you.", is_mandatory=False),
            Option("in_time", "After the specified time passes. Eg. 1h30m or 01:30.", is_mandatory=False),
            Option("at_time", "At a specific moment in time. Eg. 15:30 or 15h30m.", is_mandatory=False),
            Option("every_interval", "Repeat in intervals. Eg. 1h30m, 01:30 or day/week.", is_mandatory=False),
            Option("location", "Where you'd like to get the notification.", OptionType.INTEGER, is_mandatory=False, choices=(
                Choice("Direct message", ReminderLocation.DIRECT_MESSAGE),
                Choice("Current channel", ReminderLocation.CHANNEL)
            ))
        ),
        cooldown=Cooldown(duration=10)
    )
    async def set_reminder(
        self,
        context: ServerChatInteractionContext,
        message: str | None = None,
        in_time: str | None = None,
        at_time: str | None = None,
        every_interval: str | None = None,
        location: int = ReminderLocation.DIRECT_MESSAGE.value
    ) -> InteractionResponse:
        reminder_config = ReminderConfig(
            server_id=context.server_id,
            channel_id=context.channel_id,
            message=message,
            location=ReminderLocation(location)
        )

        try:
            if in_time is not None and len(in_time) > 0:
                reminder_config.in_time = parse_interval(in_time)
            if at_time is not None and len(at_time) > 0:
                reminder_config.at_time = parse_interval(at_time)
            if every_interval is not None and len(every_interval) > 0:
                reminder_config.every_interval = parse_interval(every_interval)
        except (InvalidInputError, ArgumentOutOfRangeError):
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.invalid_time_input_error"
                )
            )

        try:
            reminder = await self.__reminder_manager.set_reminder(context.author_id, reminder_config)
            self.__logger.debug("Set new reminder", user_id=context.author_id, reminder_id=reminder.identifier)
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.reminder_set",
                    {
                        "time": int(reminder.next_trigger.timestamp())
                    }
                )
            )
        except ArgumentOutOfRangeError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.message_out_of_range_error",
                    { "min": error.lower_bound, "max": error.upper_bound }
                )
            )
        except ArgumentError as error:
            if error.argument_name == "occurrence":
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.reminders.set_reminder_workflow.missing_time_error"
                    )
                )
            else:
                raise
        except InvalidReminderConfigError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.invalid_params_error",
                    { "param1": error.param1, "param2": error.param2 }
                )
            )
        except TooManyRemindersError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.too_many_reminders_error"
                )
            )
