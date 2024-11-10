from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class CurrenciesMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "currencies",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071726, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute("DROP INDEX ix_currencies_code_server")

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN created_by TYPE BIGINT USING created_by::BIGINT,\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id SET DEFAULT NULL"
        )

        await connection.execute(
            f"CREATE UNIQUE INDEX ix_currencies_code_server ON {self.table_name} (code, server_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} (\n"
            " id SERIAL PRIMARY KEY,\n"
            " created_at TIMESTAMP DEFAULT NOW(),\n"
            " created_by VARCHAR(20) NOT NULL,\n"
            " code VARCHAR(20) DEFAULT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " name VARCHAR(60) NOT NULL,\n"
            " description VARCHAR(120) DEFAULT NULL,\n"
            " emoji_id BIGINT NOT NULL,\n"
            " emoji_name VARCHAR(60) NOT NULL,\n"
            " is_tradable BOOLEAN NOT NULL DEFAULT FALSE\n"
            ")"
        ))

        await connection.execute((
            f"CREATE UNIQUE INDEX ix_currencies_code_server ON {self.table_name} (code, server_id)"
        ))
