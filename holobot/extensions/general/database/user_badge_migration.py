from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class UserBadgeMigration(MigrationBase):
    _TABLE_NAME = "user_badges"

    def __init__(self) -> None:
        super().__init__(UserBadgeMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {UserBadgeMigration._TABLE_NAME} ("
            " user_id VARCHAR(20) NOT NULL,\n"
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " badge_id INTEGER NOT NULL,\n"
            " unlocked_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " PRIMARY KEY(user_id, server_id, badge_id),\n"
            " CONSTRAINT fk_badges FOREIGN KEY(server_id, badge_id) REFERENCES badges(server_id, badge_id) ON DELETE CASCADE\n"
            ")"
        ))
