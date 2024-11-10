from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class QuestMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "quests",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2),
                MigrationPlan(202411071725, self.__upgrade_to_v3)
            ]
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ADD PRIMARY KEY (server_id, user_id, quest_proto_code)"
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN repeat_count SMALLINT DEFAULT NULL"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} (\n"
            " server_id VARCHAR(20) NOT NULL,\n"
            " user_id VARCHAR(20) NOT NULL,\n"
            " quest_proto_code VARCHAR(160) NOT NULL,\n"
            " completed_at TIMESTAMP DEFAULT NULL,\n"
            " objective_count_1 SMALLINT NOT NULL DEFAULT 0,\n"
            " objective_count_2 SMALLINT NOT NULL DEFAULT 0,\n"
            " PRIMARY KEY(server_id, user_id, quest_proto_code)\n"
            ")"
        ))
