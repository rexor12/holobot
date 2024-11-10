from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class UserBadgeMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "user_badges",
            [
                MigrationPlan(2, self.__initialize_table),
                MigrationPlan(202411071725, self.__upgrade_to_v2),
                MigrationPlan(202411071727, self.__upgrade_to_v3)
            ]
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD CONSTRAINT fk_user_badges_badges FOREIGN KEY (server_id, badge_id) REFERENCES badges(server_id, badge_id) ON DELETE CASCADE"
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT fk_badges")

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
            f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (user_id, server_id, badge_id)"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " user_id VARCHAR(20) NOT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " badge_id INTEGER NOT NULL,\n"
            " unlocked_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " PRIMARY KEY(user_id, server_id, badge_id),\n"
            " CONSTRAINT fk_badges FOREIGN KEY(server_id, badge_id) REFERENCES badges(server_id, badge_id) ON DELETE CASCADE\n"
            ")"
        ))
