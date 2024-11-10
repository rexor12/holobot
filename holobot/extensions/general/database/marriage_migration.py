from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class MarriageMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "marriages",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v2),
                MigrationPlan(3, self.__upgrade_to_v3),
                MigrationPlan(202411071725, self.__upgrade_to_v4)
            ]
        )

    async def __upgrade_to_v4(self, connection: Connection) -> None:
        uc_name = await self._query_unique_constraint_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {uc_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN server_id TYPE BIGINT USING server_id::BIGINT,\n"
            " ALTER COLUMN user_id1 TYPE BIGINT USING user_id1::BIGINT,\n"
            " ALTER COLUMN user_id2 TYPE BIGINT USING user_id2::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}"
            f" ADD CONSTRAINT uc_{self.table_name} UNIQUE (server_id, user_id1, user_id2)"
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}"
            " ADD COLUMN lick_count INTEGER NOT NULL DEFAULT 0,"
            " ADD COLUMN bite_count INTEGER NOT NULL DEFAULT 0,"
            " ADD COLUMN handhold_count INTEGER NOT NULL DEFAULT 0,"
            " ADD COLUMN cuddle_count INTEGER NOT NULL DEFAULT 0"
        ))

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}"
            " ADD COLUMN last_level_up_at TIMESTAMP DEFAULT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " server_id VARCHAR(20) NOT NULL,"
            " user_id1 VARCHAR(20) NOT NULL,"
            " user_id2 VARCHAR(20) NOT NULL,"
            " married_at TIMESTAMP DEFAULT (NOW() at time zone 'utc'),"
            " level INTEGER NOT NULL DEFAULT 1,"
            " exp_points INTEGER NOT NULL DEFAULT 0,"
            " last_activity_at TIMESTAMP DEFAULT NULL,"
            " activity_tier_reset_at TIMESTAMP NOT NULL,"
            " activity_tier INTEGER NOT NULL DEFAULT 0,"
            " hug_count INTEGER NOT NULL DEFAULT 0,"
            " kiss_count INTEGER NOT NULL DEFAULT 0,"
            " pat_count INTEGER NOT NULL DEFAULT 0,"
            " poke_count INTEGER NOT NULL DEFAULT 0,"
            " match_bonus INTEGER NOT NULL DEFAULT 0,"
            " UNIQUE(server_id, user_id1, user_id2)"
            ")"
        ))
