import ssl
from collections.abc import Awaitable

import asyncpg

from holobot.sdk.configs import IOptions
from holobot.sdk.database import IDatabaseManager, ISession
from holobot.sdk.database.migration import IMigration
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading.utils import COMPLETED_TASK
from holobot.sdk.utils.iterable_utils import select_many
from .database_options import DatabaseOptions
from .session import Session

@injectable(IStartable)
@injectable(IDatabaseManager)
class DatabaseManager(IDatabaseManager, IStartable):
    @property
    def priority(self) -> int:
        return 10

    def __init__(
        self,
        database_options: IOptions[DatabaseOptions],
        logger_factory: ILoggerFactory,
        migrations: tuple[IMigration, ...]
    ) -> None:
        self.__database_options = database_options
        self.__logger = logger_factory.create(DatabaseManager)
        self.__migrations: tuple[IMigration, ...] = migrations
        self.__connection_pool: asyncpg.Pool | None = None

    def start(self) -> Awaitable[None]:
        return COMPLETED_TASK

    async def stop(self) -> None:
        if self.__connection_pool:
            await self.__connection_pool.close()
        self.__logger.info("Successfully shut down")

    async def upgrade_all(self) -> None:
        self.__logger.info("Upgrading the database...")
        self.__connection_pool = await self.__initialize_database()
        async with self.__connection_pool.acquire() as connection:
            connection: asyncpg.Connection
            async with connection.transaction():
                current_version = await self.__get_current_migration_version(connection)
                sorted_plans = sorted(
                    filter(
                        lambda i: i.new_version > current_version,
                        select_many(self.__migrations, lambda i: i.plans)
                    ),
                    key=lambda i: i.new_version
                )
                new_version = current_version
                for plan in sorted_plans:
                    self.__logger.info(
                        "Applying migration...",
                        version=plan.new_version
                    )
                    await plan.execute(connection)
                    if plan.new_version > new_version:
                        new_version = plan.new_version

                if new_version != current_version:
                    await self.__update_migration_version(connection, new_version)

        self.__logger.info("Successfully upgraded the database", new_version=new_version)

    async def acquire_connection(self) -> ISession:
        assert self.__connection_pool
        connection: asyncpg.Connection = await self.__connection_pool.acquire()
        return Session(connection, self.__connection_pool)

    async def __initialize_database(self) -> asyncpg.pool.Pool:
        options = self.__database_options.value
        connection_string_base = f"postgres://{options.User}:{options.Password}@{options.Host}:{options.Port}/"
        ssl_object = self.__create_ssl_context()
        if options.AutoCreateDatabase:
            self.__logger.debug("Connecting to the database 'postgres'...")
            postgres_dsn = f"{connection_string_base}postgres"
            connection = await asyncpg.connect(postgres_dsn,ssl=ssl_object)
            self.__logger.debug("Successfully connected to the database")
            try:
                await self.__try_create_database(connection, options.Database)
            finally:
                await connection.close()

        self.__logger.debug("Initializing the connection pool...")
        pool = await asyncpg.create_pool(
            f"{connection_string_base}{options.Database}",
            ssl=ssl_object)
        if not pool:
            raise Exception("Failed to initialize the database connection pool.")
        self.__logger.debug("Successfully initialized the connection pool")

        async with pool.acquire() as connection:
            await self.__initialize_migration_table(connection)

        return pool

    def __create_ssl_context(self):
        ssl_context = None
        if self.__database_options.value.IsSslEnabled:
            ssl_context = ssl.create_default_context(cafile="")
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    async def __try_create_database(
        self,
        connection: asyncpg.Connection,
        name: str
    ) -> None:
        if await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", name) != 1:
            self.__logger.debug("Creating a new database", name=name)
            await connection.execute(f"CREATE DATABASE {name} ENCODING 'UTF8' TEMPLATE template0")
            self.__logger.debug("Successfully created the database")

    async def __initialize_migration_table(
        self,
        connection: asyncpg.Connection
    ) -> None:
        await connection.execute(
            "CREATE TABLE IF NOT EXISTS migration_info (\n"
            " singleton_key BOOLEAN DEFAULT TRUE UNIQUE,\n"
            " version BIGINT NOT NULL,\n"
            " updated_at TIMESTAMP NOT NULL\n"
            ")"
        )

        # NOTE: For a while migration versions were local to their tables,
        # but foreign references, etc. created the need to unify them.
        # Therefore, there is a bit of migration magic happening here
        # so that upgrades from older versions are seamless.
        if not await self.__table_exists(connection, "table_info"):
            return

        highest_version = await connection.fetchval(
            "SELECT MAX(version) AS highest_version FROM table_info"
        )
        if not isinstance(highest_version, int):
            raise ValueError(
                f"Couldn't determine the current migration version,"
                " because the result is not an integer value."
            )

        await self.__update_migration_version(connection, highest_version)
        await connection.execute("DROP TABLE table_info")

    async def __table_exists(
        self,
        connection: asyncpg.Connection,
        table_name: str
    ) -> bool:
        result = await connection.fetchval(
            "SELECT\n"
            "   CASE\n"
            f"       WHEN to_regclass('{table_name}') IS NULL THEN 0\n"
            "       ELSE 1\n"
            "   END as table_exists"
        )

        if not isinstance(result, int):
            raise ValueError(
                f"Couldn't determine if the table {table_name} exists,"
                " because the result is not a bool value."
            )

        return result == 1

    async def __update_migration_version(
        self,
        connection: asyncpg.Connection,
        version: int
    ) -> None:
        await connection.execute(
            "INSERT INTO migration_info (version, updated_at)\n"
            "VALUES ($1, NOW() AT TIME ZONE 'utc')\n"
            "ON CONFLICT (singleton_key)\n"
            "DO UPDATE SET\n"
            " version = $1,\n"
            " updated_at = NOW() AT TIME ZONE 'utc'",
            version
        )

    async def __get_current_migration_version(
        self,
        connection: asyncpg.Connection
    ) -> int:
        result = await connection.fetchval(
            "SELECT version FROM migration_info LIMIT 1"
        )

        if not isinstance(result, int):
            raise ValueError(
                "Couldn't determine the current migration version,"
                " because the result is not an integer value."
            )

        return result
