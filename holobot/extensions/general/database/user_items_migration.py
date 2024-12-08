from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class UserItemsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "user_items",
            (
                MigrationPlan(202411131201, self.__initialize_table),
            )
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(
            f"CREATE TABLE {self.table_name} (\n"
            " user_id BIGINT NOT NULL,\n"
            " server_id BIGINT NOT NULL,\n"
            " serial_id BIGINT NOT NULL,\n"
            " item_type INTEGER NOT NULL,\n"
            " item_id1 BIGINT DEFAULT NULL,\n"
            " item_id2 BIGINT DEFAULT NULL,\n"
            " item_id3 BIGINT DEFAULT NULL,\n"
            " item_data_json TEXT DEFAULT NULL,\n"
            " PRIMARY KEY (user_id, server_id, serial_id)"
            ")"
        )

        # TODO Create partial indexes for searching items.
        await connection.execute(
            f"CREATE INDEX ix_user_id_item_type ON {self.table_name} (user_id, item_type)"
        )
