import dateparser

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button, StackLayout
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.reminders import IReminderManager
from holobot.extensions.reminders.enums import ReminderLocation
from holobot.extensions.reminders.exceptions import (
    InvalidMessageLengthError, InvalidReminderConfigError, TooManyRemindersError
)
from holobot.extensions.reminders.models import ReminderConfig
from holobot.sdk.exceptions import ArgumentError, ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.datetime_utils import utcnow

_DATEPARSER_LANGUAGES: tuple[str, ...] = ("en",)
_DATEPARSER_SETTINGS_SINGLE = {
    "TO_TIMEZONE": "UTC",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DATES_FROM": "future"
}
_DATEPARSER_SETTINGS_RECURRING = {
    "TO_TIMEZONE": "UTC",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DATES_FROM": "future",
    "PARSERS": ["relative-time"]
}

@injectable(IWorkflow)
class SetReminderWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reminder_manager: IReminderManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(SetReminderWorkflow)
        self.__reminder_manager = reminder_manager

    @command(
        description="Sets a one-time reminder.",
        name="single",
        group_name="reminder",
        options=(
            Option("when", "When you'd like me to remind you. Eg. in 3 minutes; 1h 3m; 1hr.", is_mandatory=True),
            Option("message", "The message you'd like me to send you.", is_mandatory=False),
            Option("location", "Where you'd like to get the notification.", OptionType.INTEGER, is_mandatory=False, choices=(
                Choice("Direct message", ReminderLocation.DIRECT_MESSAGE),
                Choice("Current channel", ReminderLocation.CHANNEL)
            ))
        )
    )
    async def set_single_reminder(
        self,
        context: InteractionContext,
        when: str,
        message: str | None = None,
        location: int = ReminderLocation.DIRECT_MESSAGE.value
    ) -> InteractionResponse:
        if not when:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.invalid_time_input_error"
                )
            )

        remind_at = dateparser.parse(when, languages=_DATEPARSER_LANGUAGES, settings=_DATEPARSER_SETTINGS_SINGLE) # type: ignore
        if not remind_at or remind_at < utcnow():
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.time_input_parsing_error"
                )
            )

        server_id: str | None = None
        channel_id: str | None = None
        reminder_location = ReminderLocation.DIRECT_MESSAGE
        if isinstance(context, ServerChatInteractionContext):
            server_id = context.server_id
            channel_id = context.channel_id
            reminder_location = ReminderLocation(location)

        reminder_config = ReminderConfig(
            server_id=server_id,
            channel_id=channel_id,
            message=message,
            location=reminder_location,
            in_time=remind_at - utcnow()
        )

        return await self.__set_reminder(context.author_id, reminder_config)

    @command(
        description="Sets a recurring reminder.",
        name="recurring",
        group_name="reminder",
        options=(
            Option("interval", "The interval of the reminders. Eg. in 3 minutes; 1h 3m; 1hr.", is_mandatory=True),
            Option("message", "The message you'd like me to send you.", is_mandatory=False),
            Option("location", "Where you'd like to get the notification.", OptionType.INTEGER, is_mandatory=False, choices=(
                Choice("Direct message", ReminderLocation.DIRECT_MESSAGE),
                Choice("Current channel", ReminderLocation.CHANNEL)
            ))
        )
    )
    async def set_recurring_reminder(
        self,
        context: InteractionContext,
        interval: str,
        message: str | None = None,
        location: int = ReminderLocation.DIRECT_MESSAGE.value
    ) -> InteractionResponse:
        if not interval:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.invalid_time_input_error"
                )
            )

        base_time = utcnow()
        settings = dict(_DATEPARSER_SETTINGS_RECURRING)
        settings["RELATIVE_BASE"] = base_time
        parsed_datetime = dateparser.parse(interval, languages=_DATEPARSER_LANGUAGES, settings=settings) # type: ignore
        if not parsed_datetime or parsed_datetime < base_time:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.time_input_parsing_error"
                )
            )

        server_id: str | None = None
        channel_id: str | None = None
        reminder_location = ReminderLocation.DIRECT_MESSAGE
        if isinstance(context, ServerChatInteractionContext):
            server_id = context.server_id
            channel_id = context.channel_id
            reminder_location = ReminderLocation(location)

        reminder_config = ReminderConfig(
            server_id=server_id,
            channel_id=channel_id,
            message=message,
            location=reminder_location,
            every_interval=parsed_datetime - base_time
        )

        return await self.__set_reminder(context.author_id, reminder_config)

    async def __set_reminder(
        self,
        author_id: str,
        reminder_config: ReminderConfig
    ) -> InteractionResponse:
        try:
            reminder = await self.__reminder_manager.set_reminder(author_id, reminder_config)
            self.__logger.debug("Set new reminder", user_id=author_id, reminder_id=reminder.identifier)

            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.reminder_set",
                    {
                        "time": int(reminder.next_trigger.timestamp()),
                        "reminder_id": reminder.identifier
                    }
                ),
                components=[
                    StackLayout(
                        id="set_reminder_layout",
                        children=[
                            Button(
                                id="reminder_viewall",
                                owner_id=author_id,
                                text=self.__i18n_provider.get("common.buttons.view_all"),
                                style=ComponentStyle.PRIMARY
                            ),
                            Button(
                                id="reminder_cancel",
                                owner_id=author_id,
                                text=self.__i18n_provider.get("common.buttons.cancel"),
                                style=ComponentStyle.SECONDARY,
                                custom_data={
                                    "rid": str(reminder.identifier)
                                }
                            )
                        ]
                    )
                ]
            )
        except InvalidMessageLengthError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.set_reminder_workflow.message_out_of_range_error",
                    {
                        "min": error.lower_bound,
                        "max": error.upper_bound,
                        "actual_length": error.length
                    }
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
