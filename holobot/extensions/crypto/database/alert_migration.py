from asyncpg.connection import Connection
from holobot.dependency_injection import ServiceCollectionInterface
from holobot.database.migration import MigrationBase, MigrationPlan

TABLE_NAME = "crypto_alerts"

class AlertMigration(MigrationBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_1)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
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

    async def __upgrade_1(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {TABLE_NAME}"
            " ADD COLUMN frequency_type SMALLINT DEFAULT 0,"
            " ADD COLUMN frequency SMALLINT DEFAULT 0"
        ))
        await connection.execute((
            "CREATE FUNCTION inrange(notified_at timestamp, frequency_type smallint, frequency smallint)\n"
            "RETURNS boolean\n"
            "AS\n"
            "$$\n"
            "DECLARE\n"
            "   next_interval interval := CASE\n"
            "       WHEN frequency_type = 0 THEN (frequency::text || ' days')::interval\n"
            "       WHEN frequency_type = 1 THEN (frequency::text || ' hours')::interval\n"
            "       WHEN frequency_type = 2 THEN (frequency::text || ' minutes')::interval\n"
            "   END;\n"
            "BEGIN\n"
            "   RETURN NOW() >= notified_at + next_interval;\n"
            "END;\n"
            "$$ LANGUAGE 'plpgsql' STABLE;"
        ))
        await connection.execute((
            "CREATE FUNCTION targethit(price numeric, direction smallint, target_price numeric)\n"
            "RETURNS boolean\n"
            "AS\n"
            "$$\n"
            "BEGIN\n"
            "   RETURN (direction = 0 AND price >= target_price)\n"
            "          OR (direction = 1 AND price <= target_price);\n"
            "END;\n"
            "$$ LANGUAGE 'plpgsql' STABLE;"
        ))
        await connection.execute("UPDATE crypto_alerts SET frequency = '1'")
