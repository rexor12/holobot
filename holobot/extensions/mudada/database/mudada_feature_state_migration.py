from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class MudadaFeatureStateMigration(MigrationBase):
    _TABLE_NAME = "mudada_feature_states"

    def __init__(self) -> None:
        super().__init__(MudadaFeatureStateMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {MudadaFeatureStateMigration._TABLE_NAME} (\n"
            " id VARCHAR(250) PRIMARY KEY,\n"
            " is_enabled BOOLEAN NOT NULL DEFAULT TRUE\n"
            ")"
        ))
