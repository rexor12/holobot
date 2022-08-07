from datetime import datetime
from typing import Tuple, Optional

from asyncpg.connection import Connection

from .reminder_repository_interface import ReminderRepositoryInterface
from ..enums import DayOfWeek
from ..models import Reminder
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.queries import PaginationResult

TABLE_NAME = "reminders"

@injectable(ReminderRepositoryInterface)
class ReminderRepository(ReminderRepositoryInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def count(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result: Optional[int] = await Query.select().column("COUNT(*)").from_table(TABLE_NAME).where().field(
                    "user_id", Equality.EQUAL, user_id
                ).compile().fetchval(connection)
                return result or 0

    async def get(self, id: int) -> Optional[Reminder]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await Query.select().columns(
                    "id", "user_id", "created_at", "message", "is_repeating", "frequency_time",
                    "day_of_week", "until_date", "base_trigger", "last_trigger", "next_trigger"
                ).from_table(TABLE_NAME).where().field("id", Equality.EQUAL, id).compile().fetchrow(connection)
                return ReminderRepository.__parse_reminder(record) if record else None

    async def get_many(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await (Query
                    .select()
                    .columns(
                        "id", "user_id", "created_at", "message", "is_repeating", "frequency_time",
                        "day_of_week", "until_date", "base_trigger", "last_trigger", "next_trigger"
                    )
                    .from_table(TABLE_NAME)
                    .where()
                    .field("user_id", Equality.EQUAL, user_id)
                    .paginate("id", page_index, page_size)
                    .compile()
                    .fetch(connection)
                )

                return PaginationResult(
                    result.page_index,
                    result.page_size,
                    result.total_count,
                    [ReminderRepository.__parse_reminder(record) for record in result.records]
                )

    async def get_triggerable(self) -> Tuple[Reminder, ...]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await Query.select().columns(
                    "id", "user_id", "created_at", "message", "is_repeating", "frequency_time",
                    "day_of_week", "until_date", "base_trigger", "last_trigger", "next_trigger"
                ).from_table(TABLE_NAME).where().field(
                    "next_trigger", Equality.LESS | Equality.EQUAL, "(NOW() AT TIME ZONE 'utc')", True
                ).compile().fetch(connection)
                return tuple(ReminderRepository.__parse_reminder(record) for record in records)

    async def store(self, reminder: Reminder) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.insert().in_table(TABLE_NAME).fields(
                    ("user_id", reminder.user_id),
                    ("message", reminder.message),
                    ("is_repeating", reminder.is_repeating),
                    ("frequency_time", reminder.frequency_time),
                    ("day_of_week", reminder.day_of_week),
                    ("until_date", reminder.until_date),
                    ("base_trigger", reminder.base_trigger),
                    ("last_trigger", reminder.last_trigger),
                    ("next_trigger", reminder.next_trigger)
                ).compile().execute(connection)

    async def update_next_trigger(self, reminder_id: int, next_trigger: datetime) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.update().table(TABLE_NAME).field(
                    "next_trigger", next_trigger
                ).where().field("id", Equality.EQUAL, reminder_id).compile().execute(connection)

    async def delete(self, reminder_id: int) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field(
                    "id", Equality.EQUAL, reminder_id
                ).compile().execute(connection)

    async def delete_by_user(self, user_id: str, reminder_id: int) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM reminders WHERE user_id = $1 AND id = $2 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id, reminder_id)
                return record["deleted_count"] if record is not None else 0

    @staticmethod
    def __parse_reminder(record) -> Reminder:
        reminder = Reminder()
        reminder.id = record["id"]
        reminder.user_id = record["user_id"]
        reminder.created_at = record["created_at"]
        reminder.message = record["message"]
        reminder.is_repeating = record["is_repeating"]
        reminder.frequency_time = record["frequency_time"]
        reminder.day_of_week = DayOfWeek(record["day_of_week"])
        reminder.until_date = record["until_date"]
        reminder.base_trigger = record["base_trigger"]
        reminder.last_trigger = record["last_trigger"]
        reminder.next_trigger = record["next_trigger"]
        return reminder
