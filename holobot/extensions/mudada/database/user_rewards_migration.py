from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class UserRewardsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "user_rewards",
            [
                MigrationPlan(202501301437, self.__initialize_table)
            ],
            "mudada"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.schema_name}.{self.table_name} ("
            " id BIGINT PRIMARY KEY,\n"
            " reward_amount BIGINT NOT NULL\n"
            ")"
        ))
