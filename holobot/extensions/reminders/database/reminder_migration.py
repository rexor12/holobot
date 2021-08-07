from asyncpg.connection import Connection
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan

TABLE_NAME = "reminders"

@injectable(MigrationInterface)
class ReminderMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_to_v2)
        }, {})
    
    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            "ALTER TABLE reminders"
            " ADD COLUMN base_trigger TIMESTAMP NOT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute("DROP TABLE IF EXISTS reminders")
        await connection.execute((
            "CREATE TABLE reminders ("
            " id SERIAL PRIMARY KEY,"
            " user_id VARCHAR(20) NOT NULL,"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " message VARCHAR(120) NOT NULL,"
            " is_repeating BOOLEAN DEFAULT FALSE,"
            " frequency_time INTERVAL DEFAULT NULL," # "Specific interval"
            " day_of_week SMALLINT DEFAULT 0," # On which day (mon, tue...)
            " until_date DATE DEFAULT NULL," # Until which date to repeat
            " last_trigger TIMESTAMP NOT NULL,"
            " next_trigger TIMESTAMP NOT NULL"
            " )"
        ))
