from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class MudadaFeatureStateMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "mudada_feature_states",
            [
                MigrationPlan(1, self.__initialize_table)
            ]
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} (\n"
            " id VARCHAR(250) PRIMARY KEY,\n"
            " is_enabled BOOLEAN NOT NULL DEFAULT TRUE\n"
            ")"
        ))
