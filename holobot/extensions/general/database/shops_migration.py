from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ShopsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "shops",
            [
                MigrationPlan(202503272325, self.__initialize_table),
            ]
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " server_id BIGINT NOT NULL,\n"
            " shop_id BIGINT NOT NULL,\n"
            " shop_name TEXT DEFAULT NULL,\n"
            " valid_from TIMESTAMP WITH TIME ZONE DEFAULT NULL,\n"
            " valid_to TIMESTAMP WITH TIME ZONE DEFAULT NULL,\n"
            " PRIMARY KEY(server_id, shop_id)\n"
            ")"
        ))
