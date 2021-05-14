from asyncpg.connection import Connection
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.database.migration.migration_plan import MigrationPlan
from typing import Dict, Optional

class ReminderMigration(MigrationInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__("reminders")
        self.__plans: Dict[str, Dict[int, MigrationPlan]] = {
            "upgrades": {
                0: MigrationPlan(0, 1, self.__initialize_table)
            },
            "rollbacks": {}
        }
    
    async def upgrade(self, connection: Connection, current_version: int, target_version: Optional[int] = None) -> int:
        while (plan := self.__plans["upgrades"].get(current_version)) is not None:
            if target_version is not None and plan.new_version <= target_version:
                break
            await plan.execute(connection)
            current_version = plan.new_version
        return current_version

    async def downgrade(self, connection: Connection, current_version: int, target_version: int) -> int:
        raise NotImplementedError

    async def __initialize_table(self, connection: Connection):
        await connection.execute("DROP TABLE IF EXISTS reminders")
        await connection.execute((
            "CREATE TABLE reminders ("
            " id SERIAL PRIMARY KEY,"
            " user_id VARCHAR(20) NOT NULL,"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " message VARCHAR(120) NOT NULL,"
            " is_repeating BOOLEAN DEFAULT FALSE,"
            # Repetition related attributes
            " frequency_type SMALLINT DEFAULT 0," # None, Hourly, Daily, Weekly, Specific interval
            " frequency_time INTERVAL DEFAULT NULL," # "Specific interval"
            " day_of_week SMALLINT DEFAULT 0," # On which day (mon, tue...)
            " until_date DATE DEFAULT NULL," # Until which date to repeat
            # Single trigger
            # " trigger_date DATE DEFAULT NULL," # On which date
            # " trigger_time TIME(0) DEFAULT NULL," # At which time
            # Common
            " last_trigger TIMESTAMP NOT NULL,"
            " next_trigger TIMESTAMP NOT NULL"
            " )"
        ))