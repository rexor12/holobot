from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class QuestProtoMigration(MigrationBase):
    _TABLE_NAME = "quest_protos"

    def __init__(self):
        super().__init__(QuestProtoMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {QuestProtoMigration._TABLE_NAME} (\n"
            " server_id VARCHAR(20) NOT NULL,\n"
            " code VARCHAR(160) NOT NULL,\n"
            " reset_type SMALLINT NOT NULL DEFAULT 0,\n"
            " reset_time INTERVAL DEFAULT NULL,\n"
            " is_hidden BOOLEAN NOT NULL DEFAULT FALSE,\n"
            " objective_type_1 SMALLINT DEFAULT NULL,\n"
            " objective_target_1 BIGINT DEFAULT NULL,\n"
            " objective_count_1 SMALLINT NOT NULL DEFAULT 0,\n"
            " objective_type_2 SMALLINT DEFAULT NULL,\n"
            " objective_target_2 BIGINT DEFAULT NULL,\n"
            " objective_count_2 SMALLINT NOT NULL DEFAULT 0,\n"
            " reward_xp INTEGER NOT NULL DEFAULT 0,\n"
            " reward_sp INTEGER NOT NULL DEFAULT 0,\n"
            " reward_item_id_1 BIGINT DEFAULT NULL,\n"
            " reward_item_count_1 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_item_id_2 BIGINT DEFAULT NULL,\n"
            " reward_item_count_2 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_item_id_3 BIGINT DEFAULT NULL,\n"
            " reward_item_count_3 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_currency_id_1 BIGINT DEFAULT NULL,\n"
            " reward_currency_count_1 BIGINT NOT NULL DEFAULT 0,\n"
            " reward_currency_id_2 BIGINT DEFAULT NULL,\n"
            " reward_currency_count_2 BIGINT NOT NULL DEFAULT 0,\n"
            " title VARCHAR(120) DEFAULT NULL,\n"
            " note VARCHAR(120) DEFAULT NULL,\n"
            " completion_text VARCHAR(512) DEFAULT NULL,\n"
            " PRIMARY KEY(server_id, code)\n"
            ")"
        ))
