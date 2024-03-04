from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class CurrenciesMigration(MigrationBase):
    _TABLE_NAME = "currencies"

    def __init__(self) -> None:
        super().__init__(CurrenciesMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {CurrenciesMigration._TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,\n"
            " created_at TIMESTAMP DEFAULT NOW(),\n"
            " created_by VARCHAR(20) NOT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " name VARCHAR(60) NOT NULL,\n"
            " description VARCHAR(120) DEFAULT NULL,\n"
            " emoji_id BIGINT NOT NULL,\n"
            " emoji_name VARCHAR(60) NOT NULL,\n"
            " is_tradable BOOLEAN NOT NULL DEFAULT FALSE\n"
            ")"
        ))
