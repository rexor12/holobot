from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class MarriageMigration(MigrationBase):
    _TABLE_NAME = "marriages"

    def __init__(self) -> None:
        super().__init__(MarriageMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MarriageMigration._TABLE_NAME} ("
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
