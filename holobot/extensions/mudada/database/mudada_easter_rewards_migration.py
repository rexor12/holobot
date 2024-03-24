from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class MudadaEasterRewardsMigration(MigrationBase):
    _TABLE_NAME = "mudada_easter_rewards"

    def __init__(self) -> None:
        super().__init__(MudadaEasterRewardsMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MudadaEasterRewardsMigration._TABLE_NAME} (\n"
            " id VARCHAR(20) PRIMARY KEY,\n"
            " last_update_at TIMESTAMP DEFAULT NOW(),\n"
            " last_reward_tier SMALLINT NOT NULL\n"
            ")"
        ))
