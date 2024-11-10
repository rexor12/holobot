from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class WalletsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "wallets",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2),
                MigrationPlan(202411071727, self.__upgrade_to_v3)
            ]
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD CONSTRAINT fk_wallets_currencies FOREIGN KEY (currency_id) REFERENCES currencies(id) ON DELETE CASCADE"
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT fk_currencies")

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT,\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id SET DEFAULT NULL"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (user_id, currency_id, server_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " user_id VARCHAR(20) NOT NULL,\n"
            " currency_id BIGINT NOT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " amount INTEGER NOT NULL DEFAULT 0,\n"
            " PRIMARY KEY(user_id, currency_id, server_id),\n"
            " CONSTRAINT fk_currencies FOREIGN KEY(currency_id) REFERENCES currencies(id) ON DELETE CASCADE\n"
            ")"
        ))
