from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class SchemaMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "schema_mudada",
            [
                MigrationPlan(202501301435, self.__initialize_schema),
            ],
            "mudada"
        )

    async def __initialize_schema(self, connection: Connection) -> None:
        await connection.execute(f"CREATE SCHEMA {self.schema_name}")
