from asyncpg.connection import Connection
from holobot.dependency_injection import ServiceCollectionInterface
from holobot.database.migration import MigrationInterface, MigrationPlan
from typing import Dict, Optional

class TodoListsMigration(MigrationInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__("todo_lists")
        self.__plans: Dict[str, Dict[int, MigrationPlan]] = {
            "upgrades": {
                0: MigrationPlan(0, 1, self.__initialize_table)
            },
            "rollbacks": {}
        }
    
    async def upgrade(self, connection: Connection, current_version: int, target_version: Optional[int] = None) -> int:
        while (plan := self.__plans["upgrades"].get(current_version)) is not None:
            if target_version is not None and plan.new_version <= target_version:
                break
            await plan.execute(connection)
            current_version = plan.new_version
        return current_version

    async def downgrade(self, connection: Connection, current_version: int, target_version: int) -> int:
        raise NotImplementedError

    async def __initialize_table(self, connection: Connection):
        await connection.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        await connection.execute((
            f"CREATE TABLE {self.table_name} ("
            " id SERIAL PRIMARY KEY,"
            " user_id VARCHAR(20) NOT NULL,"
            " created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),"
            " message VARCHAR(192) NOT NULL"
            " )"
        ))
