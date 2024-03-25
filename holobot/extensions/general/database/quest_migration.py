from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class QuestMigration(MigrationBase):
    _TABLE_NAME = "quests"

    def __init__(self):
        super().__init__(QuestMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {QuestMigration._TABLE_NAME} (\n"
            " server_id VARCHAR(20) NOT NULL,\n"
            " user_id VARCHAR(20) NOT NULL,\n"
            " quest_proto_code VARCHAR(160) NOT NULL,\n"
            " completed_at TIMESTAMP DEFAULT NULL,\n"
            " objective_count_1 SMALLINT NOT NULL DEFAULT 0,\n"
            " objective_count_2 SMALLINT NOT NULL DEFAULT 0,\n"
            " PRIMARY KEY(server_id, user_id, quest_proto_code)\n"
            ")"
        ))
