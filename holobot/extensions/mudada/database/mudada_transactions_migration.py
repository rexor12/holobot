from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class MudadaTransactionsMigration(MigrationBase):
    _TABLE_NAME = "mudada_transactions"

    def __init__(self) -> None:
        super().__init__(MudadaTransactionsMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MudadaTransactionsMigration._TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,\n"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " owner_id VARCHAR(20) NOT NULL,\n"
            " target_id VARCHAR(20) NOT NULL,\n"
            " amount INTEGER NOT NULL,\n"
            " message VARCHAR(120) DEFAULT NULL,\n"
            " is_finalized BOOLEAN DEFAULT 0,\n"
            " is_completed BOOLEAN DEFAULT 0,\n"
            " UNIQUE(owner_id, target_id)\n"
            ")"
        ))
