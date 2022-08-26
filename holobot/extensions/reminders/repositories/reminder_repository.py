from typing import cast

from asyncpg.connection import Connection

from holobot.extensions.reminders.models import Reminder
from holobot.sdk.database import IDatabaseManager
from holobot.sdk.database.exceptions import DatabaseError
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag
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
    def table_name(self) -> str:
        return "reminders"

    def __init__(self, database_manager: IDatabaseManager) -> None:
        super().__init__(database_manager)

    async def count_by_user(self, user_id: str) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .select()
                    .column("COUNT(*)")
                    .from_table(self.table_name)
                    .where()
                    .field("user_id", Equality.EQUAL, user_id)
                    .compile()
                    .fetchval(connection)
                )

                return result or 0

    async def get_many(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[Reminder]:
        return await self._paginate(
            "id",
            page_index,
            page_size,
            lambda where: where.field("user_id", Equality.EQUAL, user_id)
        )

    async def get_triggerable(self) -> tuple[Reminder, ...]:
        return await self._get_many_by_filter(lambda where: (
            where.field("next_trigger", Equality.LESS_OR_EQUAL, "(NOW() AT TIME ZONE 'utc')", True)
        ))

    async def delete_by_user(self, user_id: str, reminder_id: int) -> int:
        async with self._database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .delete()
                    .from_table(self.table_name)
                    .where()
                    .fields(
                        Connector.AND,
                        ("user_id", Equality.EQUAL, user_id),
                        ("id", Equality.EQUAL, reminder_id)
                    )
                    .compile()
                    .execute(connection)
                )

                if not isinstance(result, CommandComplete):
                    raise DatabaseError("Failed to delete some records.")

                return cast(CommandComplete[DeleteCommandTag], result).command_tag.rows

    def _map_record_to_model(self, record: ReminderRecord) -> Reminder:
        return Reminder(
            identifier=record.id,
            user_id=record.user_id,
            message=record.message,
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
            id=model.identifier,
            user_id=model.user_id,
            message=model.message,
            created_at=model.created_at,
            is_repeating=model.is_repeating,
            frequency_time=model.frequency_time,
            day_of_week=model.day_of_week,
            until_date=model.until_date,
            base_trigger=model.base_trigger,
            last_trigger=model.last_trigger,
            next_trigger=model.next_trigger
        )
