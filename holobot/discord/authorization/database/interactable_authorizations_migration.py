from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class InteractableAuthorizationsMigration(MigrationBase):
    _TABLE_NAME = "interactable_authorizations"

    def __init__(self) -> None:
        super().__init__(InteractableAuthorizationsMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {InteractableAuthorizationsMigration._TABLE_NAME} (\n"
            " interactable_id VARCHAR(100) NOT NULL,\n"
            " server_id VARCHAR(20) NOT NULL,\n"
            " status BOOLEAN NOT NULL,\n"
            " PRIMARY KEY(interactable_id, server_id)\n"
            ")"
        ))
