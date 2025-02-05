from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class Valentine2025Migration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "valentine2025_ratings",
            [
                MigrationPlan(202501301436, self.__initialize_table)
            ],
            "mudada"
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.schema_name}.{self.table_name} ("
            " source_user_id BIGINT NOT NULL,\n"
            " target_user_id BIGINT NOT NULL,\n"
            " score1 INTEGER NOT NULL,\n"
            " score2 INTEGER NOT NULL,\n"
            " score3 INTEGER NOT NULL,\n"
            " score4 INTEGER NOT NULL,\n"
            " score5 INTEGER NOT NULL,\n"
            " score6 INTEGER NOT NULL,\n"
            " message VARCHAR(250) DEFAULT NULL,\n"
            " is_deleted BOOLEAN NOT NULL DEFAULT false,\n"
            " PRIMARY KEY(source_user_id, target_user_id)\n"
            ")"
        ))
