from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class ReputationCooldownsMigration(MigrationBase):
    _TABLE_NAME = "reputation_cooldowns"

    def __init__(self) -> None:
        super().__init__(ReputationCooldownsMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {ReputationCooldownsMigration._TABLE_NAME} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " last_target_user_id VARCHAR(20) NOT NULL,\n"
            " last_rep_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')\n"
            ")"
        ))
