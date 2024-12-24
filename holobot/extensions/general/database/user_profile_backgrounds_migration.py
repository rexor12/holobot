from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class UserProfileBackgroundsMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "user_profile_backgrounds",
            (
                MigrationPlan(202412211204, self.__initialize_table),
            )
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(
            f"CREATE TABLE {self.table_name} (\n"
            " id SERIAL PRIMARY KEY,\n"
            " created_at TIMESTAMP DEFAULT NOW(),\n"
            " code VARCHAR(20) NOT NULL,\n"
            " name VARCHAR(60) NOT NULL"
            ")"
        )

        await connection.execute(
            f"CREATE UNIQUE INDEX ix_backgrounds_code ON {self.table_name} (code)"
        )
