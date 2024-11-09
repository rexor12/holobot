from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class BadgeMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "badges",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(202411071726, self.__upgrade_to_v2)
            ]
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN created_by TYPE BIGINT USING created_by::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN server_id SET DEFAULT NULL"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (server_id, badge_id)"
        )

    # In the case of badges, badge_id is the index of the badge on the server's badge-map.
    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " badge_id INTEGER NOT NULL,\n"
            " created_by VARCHAR(20) NOT NULL,\n"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " name VARCHAR(120) NOT NULL,\n"
            " description VARCHAR(250) DEFAULT NULL,\n"
            " emoji_name VARCHAR(15) NOT NULL,\n"
            " emoji_id BIGINT NOT NULL,\n"
            " PRIMARY KEY(server_id, badge_id)\n"
            ")"
        ))
