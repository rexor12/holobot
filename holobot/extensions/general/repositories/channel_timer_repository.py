from collections.abc import Awaitable

from holobot.extensions.general.models import ChannelTimer
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.queries.enums import Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ichannel_timer_repository import IChannelTimerRepository
from .records import ChannelTimerRecord

@injectable(IChannelTimerRepository)
class ChannelTimerRepository(
    RepositoryBase[int, ChannelTimerRecord, ChannelTimer],
    IChannelTimerRepository
):
    @property
    def record_type(self) -> type[ChannelTimerRecord]:
        return ChannelTimerRecord

    @property
    def model_type(self) -> type[ChannelTimer]:
        return ChannelTimer

    @property
    def table_name(self) -> str:
        return "channel_timers"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def count_by_server(self, server_id: str) -> Awaitable[int]:
        return self._count_by_filter(lambda where: where.field("server_id", Equality.EQUAL, server_id))

    def paginate(self, page_index: int, page_size: int) -> Awaitable[PaginationResult[ChannelTimer]]:
        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            None
        )

    def remove_all_by_server(self, server_id: str) -> Awaitable[int]:
        return self._delete_by_filter(lambda where: where.field("server_id", Equality.EQUAL, server_id))

    def _map_record_to_model(self, record: ChannelTimerRecord) -> ChannelTimer:
        return ChannelTimer(
            identifier=record.id,
            user_id=record.user_id,
            server_id=record.server_id,
            channel_id=record.channel_id,
            base_time=record.base_time,
            countdown_interval=record.countdown_interval,
            name_template=record.name_template,
            expiry_name_template=record.expiry_name_template
        )

    def _map_model_to_record(self, model: ChannelTimer) -> ChannelTimerRecord:
        return ChannelTimerRecord(
            id=model.identifier,
            user_id=model.user_id,
            server_id=model.server_id,
            channel_id=model.channel_id,
            base_time=model.base_time,
            countdown_interval=model.countdown_interval,
            name_template=model.name_template,
            expiry_name_template=model.expiry_name_template
        )
