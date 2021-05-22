from asyncpg.connection import Connection
from holobot.dependency_injection import ServiceCollectionInterface
from holobot.database.migration import MigrationBase, MigrationPlan

TABLE_NAME = "crypto_prices"

class CryptoMigration(MigrationBase):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__(TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table)
        }, {})

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute("DROP TABLE IF EXISTS crypto_binance")
        await connection.execute((
            "CREATE TABLE crypto_binance ("
            " id SERIAL PRIMARY KEY,"
            " symbol CHAR(16) NOT NULL,"
            " price NUMERIC(64, 8) DEFAULT 0.0,"
            " timestamp TIMESTAMP"
            " )"
        ))