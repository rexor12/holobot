from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ReminderMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "reminders",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2),
                MigrationPlan(3, self.__upgrade_to_v3),
                MigrationPlan(4, self.__upgrade_to_v4),
                MigrationPlan(202411071725, self.__upgrade_to_v5)
            ]
        )

    async def __upgrade_to_v5(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id DROP DEFAULT,\n"
            " ALTER COLUMN channel_id DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT,\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN channel_id TYPE BIGINT USING channel_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id SET DEFAULT NULL,\n"
            " ALTER COLUMN channel_id SET DEFAULT NULL"
        )

    async def __upgrade_to_v4(self, connection: Connection) -> None:
        await connection.execute((
            "ALTER TABLE reminders"
            " ADD COLUMN location SMALLINT NOT NULL DEFAULT 0,"
            " ADD COLUMN server_id VARCHAR(20) DEFAULT NULL,"
            " ADD COLUMN channel_id VARCHAR(20) DEFAULT NULL"
        ))

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute("ALTER TABLE reminders ALTER COLUMN message DROP NOT NULL")

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            "ALTER TABLE reminders"
            " ADD COLUMN base_trigger TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')"
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
