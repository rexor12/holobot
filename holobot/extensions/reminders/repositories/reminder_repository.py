from collections.abc import Awaitable

from holobot.extensions.reminders.enums import ReminderLocation
from holobot.extensions.reminders.models import Reminder
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .ireminder_repository import IReminderRepository
from .records import ReminderRecord

@injectable(IReminderRepository)
class ReminderRepository(
    RepositoryBase[int, ReminderRecord, Reminder],
    IReminderRepository
):
    @property
    def record_type(self) -> type[ReminderRecord]:
        return ReminderRecord

    @property
    def model_type(self) -> type[Reminder]:
        return Reminder

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "reminders"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def count_by_user(self, user_id: str) -> Awaitable[int]:
        return self._count_by_filter(
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

    def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[Reminder]]:
        return self._paginate(
            ((RepositoryBase._ID_FIELD_NAME, Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

    def get_triggerable(self) -> Awaitable[tuple[Reminder, ...]]:
        return self._get_many_by_filter(lambda where: (
            where.field("next_trigger", Equality.LESS_OR_EQUAL, "(NOW() AT TIME ZONE 'utc')", True)
        ))

    def delete_by_user(self, user_id: str, reminder_id: int) -> Awaitable[int]:
        return self._delete_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("user_id", Equality.EQUAL, user_id),
                ("id", Equality.EQUAL, reminder_id)
            )
        )

    def _map_record_to_model(self, record: ReminderRecord) -> Reminder:
        return Reminder(
            identifier=record.id.value,
            user_id=record.user_id,
            server_id=record.server_id,
            channel_id=record.channel_id,
            message=record.message,
            location=ReminderLocation(record.location),
            created_at=record.created_at,
            is_repeating=record.is_repeating,
            frequency_time=record.frequency_time,
            day_of_week=record.day_of_week,
            until_date=record.until_date,
            base_trigger=record.base_trigger,
            last_trigger=record.last_trigger,
            next_trigger=record.next_trigger
        )

    def _map_model_to_record(self, model: Reminder) -> ReminderRecord:
        return ReminderRecord(
            id=PrimaryKey(model.identifier),
            user_id=model.user_id,
            server_id=model.server_id,
            channel_id=model.channel_id,
            message=model.message,
            location=model.location.value,
            created_at=model.created_at,
            is_repeating=model.is_repeating,
            frequency_time=model.frequency_time,
            day_of_week=model.day_of_week,
            until_date=model.until_date,
            base_trigger=model.base_trigger,
            last_trigger=model.last_trigger,
            next_trigger=model.next_trigger
        )
