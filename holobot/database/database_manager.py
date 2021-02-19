from asyncpg.connection import Connection
from asyncpg.pool import Pool, PoolAcquireContext
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.database.exceptions.database_error import DatabaseError
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.security.global_credential_manager_interface import GlobalCredentialManagerInterface
from typing import List, Tuple

import asyncio
import asyncpg
import ssl

class DatabaseManager(DatabaseManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface):
        self.__credential_manager: GlobalCredentialManagerInterface = service_collection.get(GlobalCredentialManagerInterface)
        self.__migrations: List[MigrationInterface] = service_collection.get_all(MigrationInterface)
        self.__connection_pool: Pool = asyncio.get_event_loop().run_until_complete(self.__initialize_database())
    
    async def close(self):
        await self.__connection_pool.close()
        print("[DatabaseManager] Successfully shut down.")

    async def upgrade_all(self):
        print("[DatabaseManager] Upgrading the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    await self.__upgrade_table(connection, migration)
        print("[DatabaseManager] Successfully upgraded the database.")

    async def downgrade_many(self, version_by_table: Tuple[str, int]):
        print("[DatabaseManager] Rolling back the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    # TODO Find the migration by the version_by_table.
                    await self.__downgrade_table(connection, migration)
        print("[DatabaseManager] Successfully rolled back the database.")

    def acquire_connection(self) -> PoolAcquireContext:
        return self.__connection_pool.acquire()
    
    async def __initialize_database(self) -> Pool:
        credentials = self.__credential_manager.get_many({
            "database_host": None,
            "database_port": None,
            "database_name": None,
            "database_user": None,
            "database_password": None
        })
        if None in credentials.values():
            raise DatabaseError("Some of the database configurations are missing.")

        ssl_object = self.__create_ssl_context()
        if self.__credential_manager.get("auto_create_database", "False", bool):
            print("[DatabaseManager] Connecting to the database 'postgres'...")
            postgres_dsn = "postgres://{}:{}@{}:{}/postgres".format(
                credentials["database_user"],
                credentials["database_password"],
                credentials["database_host"],
                credentials["database_port"]
            )
            connection = await asyncpg.connect(postgres_dsn,ssl=ssl_object)
            print("[DatabaseManager] Successfully connected to the database.")
            try:
                await self.__try_create_database(connection, credentials["database_name"])
            finally:
                await connection.close()

        print("[DatabaseManager] Initializing the connection pool...")
        pool = await asyncpg.create_pool("postgres://{}:{}@{}:{}/{}".format(
            credentials["database_user"],
            credentials["database_password"],
            credentials["database_host"],
            credentials["database_port"],
            credentials["database_name"]
        ), ssl=ssl_object)
        print("[DatabaseManager] Successfully initialized the connection pool.")

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
        if not self.__credential_manager.get("is_debug", "False", bool):
            ssl_context = ssl.create_default_context(cafile="")
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
    
    async def __try_create_database(self, connection: Connection, name: str):
        if await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", name) != 1:
            print(f"[DatabaseManager] Creating the database '{name}'...")
            await connection.execute(f"CREATE DATABASE {name}") # TODO Check why args isn't working.
            print("[DatabaseManager] Successfully created the database.")

    async def __upgrade_table(self, connection: Connection, migration: MigrationInterface):
        current_version = await self.__get_current_table_version(connection, migration.table_name)
        new_version = await migration.upgrade(connection, current_version)
        await self.__update_current_table_version(connection, migration.table_name, new_version)
        if new_version != current_version:
            print(f"[DatabaseManager] Upgraded table '{migration.table_name}' from version {current_version} to version {new_version}.")

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