from asyncpg.connection import Connection
from holobot.dependency_injection import ServiceCollectionInterface
from holobot.database.migration import MigrationBase, MigrationPlan

TABLE_NAME = "todo_lists"

class TodoListsMigration(MigrationBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " user_id VARCHAR(20) NOT NULL,"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " message VARCHAR(192) NOT NULL"
            " )"
        ))
