from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class QuestProtoMigration(MigrationBase):
    def __init__(self):
        super().__init__(
            "quest_protos",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2),
                MigrationPlan(3, self.__upgrade_to_v3),
                MigrationPlan(4, self.__upgrade_to_v4),
                MigrationPlan(202411071725, self.__upgrade_to_v5)
            ]
        )

    async def __upgrade_to_v5(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN reward_badge_sid_1 DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN reward_badge_sid_1 TYPE BIGINT USING reward_badge_sid_1::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            " ALTER COLUMN reward_badge_sid_1 SET DEFAULT NULL"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (server_id, code)"
        )

    async def __upgrade_to_v4(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN max_repeats SMALLINT DEFAULT NULL"
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN valid_from TIMESTAMP WITH TIME ZONE DEFAULT NULL,\n"
            " ADD COLUMN valid_to TIMESTAMP WITH TIME ZONE DEFAULT NULL"
        )

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN reward_badge_sid_1 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN reward_badge_id_1 INTEGER DEFAULT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} (\n"
            " server_id VARCHAR(20) NOT NULL,\n"
            " code VARCHAR(160) NOT NULL,\n"
            " reset_type SMALLINT NOT NULL DEFAULT 0,\n"
            " reset_time INTERVAL DEFAULT NULL,\n"
            " is_hidden BOOLEAN NOT NULL DEFAULT FALSE,\n"
            " objective_type_1 SMALLINT DEFAULT NULL,\n"
            " objective_target_1 BIGINT DEFAULT NULL,\n"
            " objective_count_1 SMALLINT NOT NULL DEFAULT 0,\n"
            " objective_type_2 SMALLINT DEFAULT NULL,\n"
            " objective_target_2 BIGINT DEFAULT NULL,\n"
            " objective_count_2 SMALLINT NOT NULL DEFAULT 0,\n"
            " reward_xp INTEGER NOT NULL DEFAULT 0,\n"
            " reward_sp INTEGER NOT NULL DEFAULT 0,\n"
            " reward_item_id_1 BIGINT DEFAULT NULL,\n"
            " reward_item_count_1 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_item_id_2 BIGINT DEFAULT NULL,\n"
            " reward_item_count_2 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_item_id_3 BIGINT DEFAULT NULL,\n"
            " reward_item_count_3 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_currency_id_1 BIGINT DEFAULT NULL,\n"
            " reward_currency_count_1 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_currency_id_2 BIGINT DEFAULT NULL,\n"
            " reward_currency_count_2 BIGINT NOT NULL DEFAULT 0,\n"
            " title VARCHAR(120) DEFAULT NULL,\n"
            " note VARCHAR(120) DEFAULT NULL,\n"
            " completion_text VARCHAR(512) DEFAULT NULL,\n"
            " PRIMARY KEY(server_id, code)\n"
            ")"
        ))
