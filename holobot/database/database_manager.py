from holobot.configs.configurator_interface import ConfiguratorInterface
from asyncpg.connection import Connection
from asyncpg.pool import Pool, PoolAcquireContext
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from typing import List, Tuple

import asyncio
import asyncpg
import ssl

class DatabaseManager(DatabaseManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__configurator: ConfiguratorInterface = service_collection.get(ConfiguratorInterface)
        self.__migrations: List[MigrationInterface] = service_collection.get_all(MigrationInterface)
        self.__log = service_collection.get(LogInterface)
        self.__connection_pool: Pool = asyncio.get_event_loop().run_until_complete(self.__initialize_database())
    
    async def close(self):
        await self.__connection_pool.close()
        self.__log.info("[DatabaseManager] Successfully shut down.")

    async def upgrade_all(self):
        self.__log.info("[DatabaseManager] Upgrading the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    await self.__upgrade_table(connection, migration)
        self.__log.info("[DatabaseManager] Successfully upgraded the database.")

    async def downgrade_many(self, version_by_table: Tuple[str, int]):
        self.__log.info("[DatabaseManager] Rolling back the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    # TODO Find the migration by the version_by_table.
                    await self.__downgrade_table(connection, migration)
        self.__log.info("[DatabaseManager] Successfully rolled back the database.")

    def acquire_connection(self) -> PoolAcquireContext:
        return self.__connection_pool.acquire()
    
    async def __initialize_database(self) -> Pool:
        database_host = self.__configurator.get("Database", "Host", "127.0.0.1")
        database_port = self.__configurator.get("Database", "Port", 5432)
        database_name = self.__configurator.get("Database", "Database", "holobot")
        database_user = self.__configurator.get("Database", "User", "postgres")
        database_password = self.__configurator.get("Database", "Password", "")

        ssl_object = self.__create_ssl_context()
        if self.__configurator.get("Database", "AutoCreateDatabase", False):
            self.__log.debug("[DatabaseManager] Connecting to the database 'postgres'...")
            postgres_dsn = f"postgres://{database_user}:{database_password}@{database_host}:{database_port}/postgres"
            connection = await asyncpg.connect(postgres_dsn,ssl=ssl_object)
            self.__log.debug("[DatabaseManager] Successfully connected to the database.")
            try:
                await self.__try_create_database(connection, database_name)
            finally:
                await connection.close()

        self.__log.debug("[DatabaseManager] Initializing the connection pool...")
        pool = await asyncpg.create_pool(
            f"postgres://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}",
            ssl=ssl_object)
        self.__log.debug("[DatabaseManager] Successfully initialized the connection pool.")

        async with pool.acquire() as connection:
            await connection.execute((
                "CREATE TABLE IF NOT EXISTS table_info ("
                " id SERIAL PRIMARY KEY,"
                " name VARCHAR NOT NULL UNIQUE,"
                " version INTEGER DEFAULT 0"
                " )"
            ))

        return pool

    def __create_ssl_context(self):
        ssl_context = None
        if not self.__configurator.get("General", "IsDebug", False):
            ssl_context = ssl.create_default_context(cafile="")
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
    
    async def __try_create_database(self, connection: Connection, name: str):
        if await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", name) != 1:
            self.__log.debug(f"[DatabaseManager] Creating the database '{name}'...")
            await connection.execute(f"CREATE DATABASE {name} ENCODING 'UTF8' TEMPLATE template0") # TODO Check why args isn't working.
            self.__log.debug("[DatabaseManager] Successfully created the database.")

    async def __upgrade_table(self, connection: Connection, migration: MigrationInterface):
        current_version = await self.__get_current_table_version(connection, migration.table_name)
        new_version = await migration.upgrade(connection, current_version)
        await self.__update_current_table_version(connection, migration.table_name, new_version)
        if new_version != current_version:
            self.__log.debug(f"[DatabaseManager] Upgraded table '{migration.table_name}' from version {current_version} to version {new_version}.")

    async def __downgrade_table(self, connection: Connection, migration: MigrationInterface):
        # TODO Implement database rollbacks.
        raise NotImplementedError
    
    async def __get_current_table_version(self, connection: Connection, table_name: str):
        return await connection.fetchval("SELECT version FROM table_info WHERE name = $1", table_name) or 0
    
    async def __update_current_table_version(self, connection: Connection, table_name: str, version: int):
        await connection.execute((
            "INSERT INTO table_info (name, version)"
            " VALUES ($1, $2)"
            " ON CONFLICT (name) DO"
            " UPDATE SET version = $2"
        ), table_name, version)
