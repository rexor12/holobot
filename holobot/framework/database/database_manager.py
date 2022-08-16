from collections.abc import Generator
from types import coroutine

import asyncio
import ssl

from asyncpg.connection import Connection
from asyncpg.pool import Pool, PoolAcquireContext

import asyncpg

from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.migration import MigrationInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory

@injectable(IStartable)
@injectable(DatabaseManagerInterface)
class DatabaseManager(DatabaseManagerInterface, IStartable):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        migrations: tuple[MigrationInterface, ...],
        logger_factory: ILoggerFactory
    ) -> None:
        self.__configurator: ConfiguratorInterface = configurator
        self.__migrations: tuple[MigrationInterface, ...] = migrations
        self.__logger = logger_factory.create(DatabaseManager)
        self.__connection_pool: Pool = asyncio.get_event_loop().run_until_complete(self.__initialize_database())

    @coroutine
    def start(self) -> Generator[None, None, None]:
        yield

    async def stop(self):
        await self.__connection_pool.close()
        self.__logger.info("Successfully shut down")

    async def upgrade_all(self):
        self.__logger.info("Upgrading the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    await self.__upgrade_table(connection, migration)
        self.__logger.info("Successfully upgraded the database")

    async def downgrade_many(self, version_by_table: tuple[str, int]):
        self.__logger.info("Rolling back the database...")
        async with self.__connection_pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                for migration in self.__migrations:
                    # TODO Find the migration by the version_by_table.
                    await self.__downgrade_table(connection, migration)
        self.__logger.info("Successfully rolled back the database")

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
            self.__logger.debug("Connecting to the database 'postgres'...")
            postgres_dsn = f"postgres://{database_user}:{database_password}@{database_host}:{database_port}/postgres"
            connection = await asyncpg.connect(postgres_dsn,ssl=ssl_object)
            self.__logger.debug("Successfully connected to the database")
            try:
                await self.__try_create_database(connection, database_name)
            finally:
                await connection.close()

        self.__logger.debug("Initializing the connection pool...")
        pool = await asyncpg.create_pool(
            f"postgres://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}",
            ssl=ssl_object)
        if not pool:
            raise Exception("Failed to initialize the database connection pool.")
        self.__logger.debug("Successfully initialized the connection pool")

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
            self.__logger.debug("Creating a new database", name=name)
            await connection.execute(f"CREATE DATABASE {name} ENCODING 'UTF8' TEMPLATE template0") # TODO Check why args isn't working.
            self.__logger.debug("Successfully created the database")

    async def __upgrade_table(self, connection: Connection, migration: MigrationInterface):
        current_version = await self.__get_current_table_version(connection, migration.table_name)
        new_version = await migration.upgrade(connection, current_version)
        await self.__update_current_table_version(connection, migration.table_name, new_version)
        if new_version != current_version:
            self.__logger.debug(
                "Successfully upgraded table",
                name=migration.table_name,
                old_version=current_version,
                new_version=new_version
            )

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
