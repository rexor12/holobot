from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class UserProfilesMigration(MigrationBase):
    _TABLE_NAME = "user_profiles"

    def __init__(self) -> None:
        super().__init__(UserProfilesMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_to_v1),
            2: MigrationPlan(2, 3, self.__upgrade_to_v2)
        }, {})

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {UserProfilesMigration._TABLE_NAME}\n"
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
            " ADD COLUMN badge_id6 BIGINT DEFAULT NULL\n"
        ))

    async def __upgrade_to_v1(self, connection: Connection) -> None:
        await connection.execute((
            f"ALTER TABLE {UserProfilesMigration._TABLE_NAME}\n"
            " ADD COLUMN background_image_code VARCHAR(10) DEFAULT NULL"
        ))

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {UserProfilesMigration._TABLE_NAME} ("
            " id VARCHAR(20) PRIMARY KEY,\n"
            " reputation_points BIGINT NOT NULL DEFAULT 0\n"
            ")"
        ))
