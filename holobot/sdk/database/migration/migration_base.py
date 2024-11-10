from collections.abc import Sequence

from asyncpg.connection import Connection

from .imigration import IMigration
from .models.migration_plan import MigrationPlan

class MigrationBase(IMigration):
    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def plans(self) -> Sequence[MigrationPlan]:
        return self.__plans

    def __init__(
        self,
        table_name: str,
        plans: Sequence[MigrationPlan]
    ):
        super().__init__()
        if not table_name:
            raise ValueError("The specified table name is invalid.")

        self.__table_name = table_name
        self.__plans = plans

    async def _execute_script(self, connection: Connection, path: str) -> None:
        with open(path, "r", encoding="utf8") as f:
            await connection.execute(f.read())

    async def _query_primary_key_name(
        self,
        connection: Connection,
        table_name: str,
        namespace: str = "public"
    ) -> str | None:
        result = await connection.fetchval(
            "SELECT conname AS constraint_name\n"
            "FROM pg_constraint\n"
            "JOIN pg_class ON conrelid = pg_class.oid\n"
            "JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid\n"
            "WHERE contype = 'p'\n"
            f" AND pg_class.relname = '{table_name}' AND pg_namespace.nspname = '{namespace}'"
        )

        if not isinstance(result, str):
            raise ValueError(f"Unexpected value for primary key constraint name query: {result}")

        return result

    async def _query_unique_constraint_name(
        self,
        connection: Connection,
        table_name: str,
        namespace: str = "public"
    ):
        result = await connection.fetchval(
            "SELECT conname\n"
            "FROM pg_constraint\n"
            "JOIN pg_class ON conrelid = pg_class.oid\n"
            "JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid\n"
            "WHERE contype = 'u'\n"
            f" AND relname = '{table_name}' AND pg_namespace.nspname = '{namespace}'"
        )

        if not isinstance(result, str):
            raise ValueError(f"Unexpected value for unique constraint name query: {result}")

        return result
