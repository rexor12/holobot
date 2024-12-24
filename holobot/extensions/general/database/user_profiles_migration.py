from asyncpg.connection import Connection

from holobot.sdk.database.migration import IMigration, MigrationBase
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(IMigration)
class UserProfilesMigration(MigrationBase):
    def __init__(self) -> None:
        super().__init__(
            "user_profiles",
            [
                MigrationPlan(1, self.__initialize_table),
                MigrationPlan(2, self.__upgrade_to_v1),
                MigrationPlan(3, self.__upgrade_to_v2),
                MigrationPlan(202411071725, self.__upgrade_to_v3),
                MigrationPlan(202412211203, self.__upgrade_to_v4)
            ]
        )

    async def __upgrade_to_v4(self, connection: Connection) -> None:
        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            "DROP COLUMN background_image_code,\n"
            "ADD COLUMN background_image_id BIGINT DEFAULT NULL"
        )

    async def __upgrade_to_v3(self, connection: Connection) -> None:
        pk_name = await self._query_primary_key_name(connection, self.table_name)
        await connection.execute(f"ALTER TABLE {self.table_name} DROP CONSTRAINT {pk_name}")

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN badge_sid1 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid2 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid3 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid4 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid5 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid6 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid7 DROP DEFAULT,\n"
            " ALTER COLUMN badge_sid8 DROP DEFAULT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN id TYPE BIGINT USING id::BIGINT,\n"
            " ALTER COLUMN badge_sid1 TYPE BIGINT USING badge_sid1::BIGINT,\n"
            " ALTER COLUMN badge_sid2 TYPE BIGINT USING badge_sid2::BIGINT,\n"
            " ALTER COLUMN badge_sid3 TYPE BIGINT USING badge_sid3::BIGINT,\n"
            " ALTER COLUMN badge_sid4 TYPE BIGINT USING badge_sid4::BIGINT,\n"
            " ALTER COLUMN badge_sid5 TYPE BIGINT USING badge_sid5::BIGINT,\n"
            " ALTER COLUMN badge_sid6 TYPE BIGINT USING badge_sid6::BIGINT,\n"
            " ALTER COLUMN badge_sid7 TYPE BIGINT USING badge_sid7::BIGINT,\n"
            " ALTER COLUMN badge_sid8 TYPE BIGINT USING badge_sid8::BIGINT"
        )

        await connection.execute(
            f"ALTER TABLE {self.table_name}\n"
            " ALTER COLUMN badge_sid1 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid2 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid3 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid4 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid5 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid6 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid7 SET DEFAULT NULL,\n"
            " ALTER COLUMN badge_sid8 SET DEFAULT NULL"
        )

        await connection.execute(f"ALTER TABLE {self.table_name} ADD PRIMARY KEY (id)")

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN show_badges BOOLEAN DEFAULT true,\n"
            " ADD COLUMN badge_sid1 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id1 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid2 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id2 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid3 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id3 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid4 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id4 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid5 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id5 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid6 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id6 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid7 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id7 BIGINT DEFAULT NULL,\n"
            " ADD COLUMN badge_sid8 VARCHAR(20) DEFAULT NULL,\n"
            " ADD COLUMN badge_id8 BIGINT DEFAULT NULL\n"
        ))

    async def __upgrade_to_v1(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {self.table_name}\n"
            " ADD COLUMN background_image_code VARCHAR(10) DEFAULT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " reputation_points BIGINT NOT NULL DEFAULT 0\n"
            ")"
        ))
