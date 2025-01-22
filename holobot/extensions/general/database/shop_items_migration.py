from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class ShopItemsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "shop_items",
            [
                MigrationPlan(202501171054, self.__initialize_table),
            ]
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " server_id BIGINT NOT NULL,\n"
            " shop_id BIGINT NOT NULL,\n"
            " serial_id BIGINT NOT NULL,\n"
            " item_type INTEGER NOT NULL,\n"
            " item_id1 BIGINT NOT NULL,\n"
            " item_id2 BIGINT DEFAULT NULL,\n"
            " item_id3 BIGINT DEFAULT NULL,\n"
            " count INTEGER DEFAULT 1,\n"
            " price_currency_id BIGINT NOT NULL,\n"
            " price_amount INTEGER NOT NULL,\n"
            " PRIMARY KEY(server_id, shop_id, serial_id),\n"
            " CONSTRAINT fk_shops FOREIGN KEY(server_id, shop_id) REFERENCES shops(server_id, shop_id) ON DELETE CASCADE\n"
            ")"
        ))
