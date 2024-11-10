import asyncio
from collections.abc import Awaitable
from datetime import timedelta

from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, ServerNotFoundError
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.extensions.general.models import ChannelTimer
from holobot.extensions.general.repositories import IChannelTimerRepository
from holobot.sdk.ioc import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.logging.enums.log_level import LogLevel
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import COMPLETED_TASK, wait
from holobot.sdk.utils.datetime_utils import utcnow
from holobot.sdk.utils.timedelta_utils import format_timedelta

_REFRESH_INTERVAL: timedelta = timedelta(minutes=5)

@injectable(IStartable)
class ChannelTimerProcessor(IStartable):
    def __init__(
        self,
        channel_manager: IChannelManager,
        channel_timer_repository: IChannelTimerRepository,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ChannelTimerProcessor)
        self.__channel_manager = channel_manager
        self.__channel_timer_repository = channel_timer_repository
        self.__token_source: CancellationTokenSource | None = None
        self.__background_task: Awaitable[None] | None = None

    @property
    def priority(self) -> int:
        return 1000

    def start(self) -> Awaitable[None]:
        self.__logger.info("Channel timers are enabled")
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__process_items(self.__token_source.token)
        )
        return COMPLETED_TASK

    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__logger.debug("Stopped channel timer processor")

    async def __process_items(self, token: CancellationToken):
        await wait(30, token)
        while not token.is_cancellation_requested:
            self.__logger.trace("Processing channel timers...")
            processed_items: int = 0
            try:
                page_index = 0
                has_items = True
                while has_items:
                    pagination = await self.__channel_timer_repository.paginate(page_index, 5)
                    for item in pagination.items:
                        await self.__try_process_item(item)
                        processed_items += 1

                    has_items = pagination.total_count > (page_index + 1) * pagination.page_size
                    page_index += 1
            except Exception as error:
                self.__logger.error("Unexpected failure while processing channel timers", error)
            finally:
                self.__logger.trace("Processed channel timers", count=processed_items)
            await wait(int(_REFRESH_INTERVAL.total_seconds()) + 5, token)

    async def __try_process_item(self, item: ChannelTimer) -> None:
        try:
            await self.__process_item(item)
        except (ChannelNotFoundError, ServerNotFoundError, ForbiddenError) as error:
            self.__logger.warning(
                "Failed to process a channel timer due to an unrecoverable error, will not retry",
                error,
                timer_id=item.identifier,
                owner_id=item.user_id,
                server_id=item.server_id,
                channel_id=item.channel_id
            )
            await self.__channel_timer_repository.delete(item.identifier)

    async def __process_item(self, item: ChannelTimer) -> None:
        now = utcnow()
        total_elapsed_time = now - item.base_time
        cycle_count = int(total_elapsed_time.total_seconds() / item.countdown_interval.total_seconds())
        remaining_time = item.base_time + (cycle_count + 1) * item.countdown_interval - now
        name_template = (
            item.name_template
            if remaining_time > _REFRESH_INTERVAL or not item.expiry_name_template
            else item.expiry_name_template
        )

        if not name_template:
            name_template = "%t"

        time_template = (
            "{hours:,.0f}h {minutes:,.0f}m"
            if remaining_time.total_seconds() >= 3600
            else "{minutes:,.0f}m"
        )

        if (self.__logger.is_log_level_enabled(LogLevel.TRACE)):
            self.__logger.trace(
                "Updating channel timer",
                server_id=item.server_id,
                channel_id=item.channel_id,
                name_template=time_template,
                remaining_seconds=remaining_time.total_seconds()
            )

        await self.__channel_manager.change_channel_name(
            item.server_id,
            item.channel_id,
            name_template.replace(
                "%t",
                format_timedelta(remaining_time, "-", time_template),
                1
            )
        )
