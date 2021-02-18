from asyncpg.connection import Connection
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.database.migration.migration_base import MigrationBase
from holobot.database.migration.migration_plan import MigrationPlan

TABLE_NAME = "crypto_alerts"

class AlertMigration(MigrationBase):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection):
        await connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        await connection.execute((
            f"CREATE TABLE {TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,"
            " created_at TIMESTAMP DEFAULT NOW(),"
            " user_id VARCHAR(20) NOT NULL,"
            " symbol CHAR(16) NOT NULL,"
            " direction SMALLINT DEFAULT 0,"
            " price NUMERIC(64, 8) DEFAULT 0.0,"
            " notified_at TIMESTAMP DEFAULT NOW()"
            " )"
        ))