from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class WalletsMigration(MigrationBase):
    _TABLE_NAME = "wallets"

    def __init__(self) -> None:
        super().__init__(WalletsMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {WalletsMigration._TABLE_NAME} ("
            " user_id VARCHAR(20) NOT NULL,\n"
            " currency_id BIGINT NOT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " amount INTEGER NOT NULL DEFAULT 0,\n"
            " PRIMARY KEY(user_id, currency_id, server_id),\n"
            " CONSTRAINT fk_currencies FOREIGN KEY(currency_id) REFERENCES currencies(id) ON DELETE CASCADE\n"
            ")"
        ))
