from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class BadgeMigration(MigrationBase):
    _TABLE_NAME = "badges"

    def __init__(self) -> None:
        super().__init__(BadgeMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    # In the case of badges, badge_id is the index of the badge on the server's badge-map.
    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {BadgeMigration._TABLE_NAME} ("
            " server_id VARCHAR(20) DEFAULT NULL,\n"
            " badge_id INTEGER NOT NULL,\n"
            " created_by VARCHAR(20) NOT NULL,\n"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),\n"
            " name VARCHAR(120) NOT NULL,\n"
            " description VARCHAR(250) DEFAULT NULL,\n"
            " emoji_name VARCHAR(15) NOT NULL,\n"
            " emoji_id BIGINT NOT NULL,\n"
            " PRIMARY KEY(server_id, badge_id)\n"
            ")"
        ))
