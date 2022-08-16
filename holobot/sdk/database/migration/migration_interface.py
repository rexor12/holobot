from asyncpg.connection import Connection

class MigrationInterface:
    def __init__(self, table_name: str):
        if not table_name or len(table_name) == 0:
            raise ValueError("The specified table name is invalid.")
        self.table_name = table_name

    # NOTE When upgrading tables, the target version may be omitted
    # in which case the latest version is favored.
    async def upgrade(self, connection: Connection, current_version: int, target_version: int | None = None) -> int:
        raise NotImplementedError

    # NOTE When rolling back upgrades, the target version is always required.
    async def downgrade(self, connection: Connection, current_version: int, target_version: int) -> int:
        raise NotImplementedError
