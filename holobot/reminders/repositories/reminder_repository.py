from asyncpg.connection import Connection
from datetime import datetime
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.reminders.enums.day_of_week import DayOfWeek
from holobot.reminders.enums.frequency_type import FrequencyType
from holobot.reminders.models.reminder import Reminder
from holobot.reminders.repositories.reminder_repository_interface import ReminderRepositoryInterface
from typing import List, Optional

class ReminderRepository(ReminderRepositoryInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        self.__database_manager: DatabaseManagerInterface = service_collection.get(DatabaseManagerInterface)
        
    async def count(self, user_id: str) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result: Optional[int] = await connection.fetchval("SELECT COUNT(*) FROM reminders WHERE user_id = $1", user_id)
                return result or 0

    async def get(self, id: int) -> Optional[Reminder]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                result = await connection.fetchrow((
                    "SELECT id, user_id, created_at, message, is_repeating, frequency_type,"
                    " frequency_time, day_of_week, until_date, last_trigger, next_trigger"
                    " FROM reminders WHERE id = $1"
                ), id)
                if result is None:
                    return None
                return ReminderRepository.__parse_reminder(result)
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> List[Reminder]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch((
                    "SELECT id, user_id, created_at, message, is_repeating, frequency_type,"
                    " frequency_time, day_of_week, until_date, last_trigger, next_trigger"
                    " FROM reminders WHERE user_id = $1 LIMIT $3 OFFSET $2"
                ), user_id, start_offset, page_size)
                return [ReminderRepository.__parse_reminder(record) for record in records]

    async def get_triggerable(self) -> List[Reminder]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch((
                    "SELECT id, user_id, created_at, message, is_repeating, frequency_type,"
                    " frequency_time, day_of_week, until_date, last_trigger, next_trigger"
                    " FROM reminders WHERE next_trigger <= (NOW() AT TIME ZONE 'utc')"
                ))
                return [ReminderRepository.__parse_reminder(record) for record in records]

    async def store(self, reminder: Reminder) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await connection.execute((
                    "INSERT INTO reminders (user_id, message, is_repeating, frequency_type,"
                    " frequency_time, day_of_week, until_date, last_trigger, next_trigger)"
                    " VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
                ), reminder.user_id, reminder.message, reminder.is_repeating,
                reminder.frequency_type, reminder.frequency_time, reminder.day_of_week,
                reminder.until_date, reminder.last_trigger, reminder.next_trigger)
    
    async def update_next_trigger(self, reminder_id: int, next_trigger: datetime) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await connection.execute("UPDATE reminders SET next_trigger = $2 WHERE id = $1", reminder_id, next_trigger)

    async def delete(self, reminder_id: int) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await connection.execute("DELETE FROM reminders WHERE id = $1", reminder_id)
    
    async def delete_by_user(self, user_id: str, reminder_id: int) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "WITH deleted AS"
                    " (DELETE FROM reminders WHERE user_id = $1 AND id = $2 RETURNING *)"
                    " SELECT COUNT(*) AS deleted_count FROM deleted"
                ), user_id, reminder_id)
                return record["deleted_count"]
    
    @staticmethod
    def __parse_reminder(record) -> Reminder:
        reminder = Reminder()
        reminder.id = record["id"]
        reminder.user_id = record["user_id"]
        reminder.created_at = record["created_at"]
        reminder.message = record["message"]
        reminder.is_repeating = record["is_repeating"]
        reminder.frequency_type = FrequencyType(record["frequency_type"])
        reminder.frequency_time = record["frequency_time"]
        reminder.day_of_week = DayOfWeek(record["day_of_week"])
        reminder.until_date = record["until_date"]
        reminder.last_trigger = record["last_trigger"]
        reminder.next_trigger = record["next_trigger"]
        return reminder
