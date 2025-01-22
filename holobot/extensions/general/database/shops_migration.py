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
                MigrationPlan(202501171053, self.__initialize_table),
            ]
        )

    async def __initialize_table(self, connection: Connection) -> None:
        # TODO (Shops) valid from+to, like quests
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " server_id BIGINT NOT NULL,\n"
            " shop_id BIGINT NOT NULL,\n"
            " shop_name TEXT DEFAULT NULL,\n"
            " PRIMARY KEY(server_id, shop_id)\n"
            ")"
        ))
