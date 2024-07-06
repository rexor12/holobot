from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class MudadaExchangeQuotasMigration(MigrationBase):
    _TABLE_NAME = "mudada_exchange_quotas"

    def __init__(self) -> None:
        super().__init__(MudadaExchangeQuotasMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MudadaExchangeQuotasMigration._TABLE_NAME} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " amount INTEGER NOT NULL DEFAULT 0,\n"
            " exchanged_amount INTEGER NOT NULL DEFAULT 0,\n"
            " lost_amount INTEGER NOT NULL DEFAULT 0\n"
            ")"
        ))
