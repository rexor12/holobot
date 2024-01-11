from datetime import datetime

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.exceptions import ChannelNotFoundError
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import ChannelTimer
from holobot.extensions.general.repositories import IChannelTimerRepository
from holobot.sdk.chrono import InvalidInputError, parse_interval
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

_BASE_TIME_MAX_SECONDS: int = 23 * 3600 + 59 * 60 # 23:59
_INTERVAL_MAX_SECONDS: int = 24 * 3600 # 24 hours
_INTERVAL_MIN_SECONDS: int = 10 * 60 # 10 minutes
_NAME_TEMPLATE_LENGTH_MAX: int = 15

# This is a hard limit, because Discord enforces a rate limit of 2 channel edits/10 minutes.
_TIMERS_PER_SERVER_MAX: int = 1

@injectable(IWorkflow)
class CreateChannelTimerWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        channel_manager: IChannelManager,
        channel_timer_repository: IChannelTimerRepository,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__channel_manager = channel_manager
        self.__channel_timer_repository = channel_timer_repository
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="timers",
        name="create",
        description="Creates a new channel timer.",
        required_permissions=Permission.ADMINISTRATOR,
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        is_ephemeral=True,
        options=(
            Option("base_time", "The time of the day, in UTC, when the timer would first begin, in HH:MM format (24-hour)."),
            Option("interval", "The repeat interval of the timer from which the countdown begins, in HH:MM format (24-hour)."),
            Option("channel", "The voice channel to use as the timer.", OptionType.CHANNEL),
            Option("name_template", "The template used for naming the channel. Use %t for the time.", is_mandatory=False),
            Option("expiry_name_template", "The template used for naming the channel when less than 5 minutes are left.", is_mandatory=False)
        ),
        cooldown=Cooldown(duration=3)
    )
    async def create_channel_timer(
        self,
        context: InteractionContext,
        base_time: str,
        interval: str,
        channel: int,
        name_template: str | None = None,
        expiry_name_template: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                is_ephemeral=True
            )

        try:
            base_time_parsed = parse_interval(base_time)
            interval_parsed = parse_interval(interval)
        except InvalidInputError:
            return self._reply(
                content=self.__i18n.get("extensions.general.create_channel_timer_workflow.time_input_parsing_error"),
                is_ephemeral=True
            )

        if base_time_parsed.total_seconds() > _BASE_TIME_MAX_SECONDS or base_time_parsed.total_seconds() < 0:
            return self._reply(
                content=self.__i18n.get("extensions.general.create_channel_timer_workflow.base_time_out_of_range_error"),
                is_ephemeral=True
            )

        if interval_parsed.total_seconds() > _INTERVAL_MAX_SECONDS or interval_parsed.total_seconds() < _INTERVAL_MIN_SECONDS:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.create_channel_timer_workflow.interval_out_of_range_error",
                    {
                        "minutes_min": _INTERVAL_MIN_SECONDS / 60,
                        "minutes_max": _INTERVAL_MAX_SECONDS / 60
                    }
                ),
                is_ephemeral=True
            )

        channel_id = str(channel)
        try:
            server_channel = await self.__channel_manager.get_channel_by_id(context.server_id, channel_id)
            if not server_channel.is_voice:
                return self._reply(
                    content="extensions.general.create_channel_timer_workflow.invalid_channel_error"
                )
        except ChannelNotFoundError:
            return self._reply(content=self.__i18n.get("channel_not_found_error"), is_ephemeral=True)

        if name_template and (len(name_template) > _NAME_TEMPLATE_LENGTH_MAX or "%t" not in name_template):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.create_channel_timer_workflow.invalid_name_template_error",
                    {
                        "max_length": _NAME_TEMPLATE_LENGTH_MAX
                    }
                ),
                is_ephemeral=True
            )

        if expiry_name_template and len(expiry_name_template) > _NAME_TEMPLATE_LENGTH_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.create_channel_timer_workflow.invalid_expiry_name_template_error",
                    {
                        "max_length": _NAME_TEMPLATE_LENGTH_MAX
                    }
                ),
                is_ephemeral=True
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            if await self.__channel_timer_repository.count_by_server(context.server_id) >= _TIMERS_PER_SERVER_MAX:
                return self._reply(
                content=self.__i18n.get(
                    "extensions.general.create_channel_timer_workflow.too_many_timers_error",
                    {
                        "max_timers": _TIMERS_PER_SERVER_MAX
                    }
                ),
                is_ephemeral=True
            )

            now = utcnow()
            base_minutes, base_seconds = divmod(base_time_parsed.total_seconds(), 60)
            base_hours, base_minutes = divmod(base_minutes, 60)
            await self.__channel_timer_repository.add(ChannelTimer(
                user_id=context.author_id,
                server_id=context.server_id,
                channel_id=channel_id,
                base_time=datetime(
                    now.year,
                    now.month,
                    now.day,
                    int(base_hours),
                    int(base_minutes),
                    int(base_seconds)
                ),
                countdown_interval=interval_parsed,
                name_template=name_template,
                expiry_name_template=expiry_name_template
            ))

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.create_channel_timer_workflow.timer_created_successfully"
            )
        )
