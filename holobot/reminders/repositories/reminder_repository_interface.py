from asyncpg.connection import Connection
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.reminders.enums.day_of_week import DayOfWeek
from holobot.reminders.enums.frequency_type import FrequencyType
from holobot.reminders.models.reminder import Reminder
from typing import Optional

class ReminderRepositoryInterface:
    async def count(self, user_id: str) -> int:
        raise NotImplementedError

    async def get(self, id: int) -> Optional[Reminder]:
        raise NotImplementedError

    async def store(self, reminder: Reminder) -> None:
        raise NotImplementedError

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
                    "SELECT id, user_id, is_repeating, frequency_type, frequency_time,"
                    " day_of_week, until_date, next_trigger"
                    " FROM reminders WHERE id = $1"
                ), id)
                if result is None:
                    return None

                reminder = Reminder()
                reminder.id = result["id"]
                reminder.user_id = result["user_id"]
                reminder.is_repeating = result["is_repeating"]
                reminder.frequency_type = FrequencyType(result["frequency_type"])
                reminder.frequency_time = result["frequency_time"]
                reminder.day_of_week = DayOfWeek(result["day_of_week"])
                reminder.until_date = result["until_date"]
                reminder.next_trigger = result["next_trigger"]
                return reminder

    async def store(self, reminder: Reminder) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await connection.execute((
                    "INSERT INTO reminders (user_id, is_repeating, frequency_type,"
                    " frequency_time, day_of_week, until_date, next_trigger)"
                    " VALUES ($1, $2, $3, $4, $5, $6, $7)"
                ), reminder.user_id, reminder.is_repeating, reminder.frequency_type,
                reminder.frequency_time, reminder.day_of_week, reminder.until_date, reminder.next_trigger)