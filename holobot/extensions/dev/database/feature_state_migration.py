from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class FeatureStateMigration(MigrationBase):
    _TABLE_NAME = "feature_states"

    def __init__(self) -> None:
        super().__init__(FeatureStateMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {FeatureStateMigration._TABLE_NAME} ("
            " id VARCHAR(250) PRIMARY KEY,"
            " is_enabled BOOLEAN NOT NULL DEFAULT TRUE"
            ")"
        ))
