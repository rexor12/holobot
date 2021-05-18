from asyncpg.connection import Connection
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.database.migration.migration_plan import MigrationPlan
from typing import Optional

class CryptoMigration(MigrationInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        super().__init__("crypto_prices")
        self.__plans = {
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
        await connection.execute("DROP TABLE IF EXISTS crypto_binance")
        await connection.execute((
            "CREATE TABLE crypto_binance ("
            " id SERIAL PRIMARY KEY,"
            " symbol CHAR(16) NOT NULL,"
            " price NUMERIC(64, 8) DEFAULT 0.0,"
            " timestamp TIMESTAMP"
            " )"
        ))