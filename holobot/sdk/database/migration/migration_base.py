from asyncpg.connection import Connection

from .migration_interface import MigrationInterface
from .models.migration_plan import MigrationPlan

class MigrationBase(MigrationInterface):
    def __init__(self, table_name: str, upgrade_plans: dict[int, MigrationPlan], downgrade_plans: dict[int, MigrationPlan]):
        super().__init__(table_name)
        self.__upgrade_plans = upgrade_plans
        self.__downgrade_plans = downgrade_plans

    async def upgrade(self, connection: Connection, current_version: int, target_version: int | None = None) -> int:
        while (plan := self.__upgrade_plans.get(current_version)) is not None:
            if target_version is not None and plan.new_version > target_version:
                break
            await plan.execute(connection)
            current_version = plan.new_version
        return current_version

    async def downgrade(self, connection: Connection, current_version: int, target_version: int) -> int:
        while (plan := self.__downgrade_plans.get(current_version)):
            if plan.new_version < target_version:
                break
            await plan.execute(connection)
            current_version = plan.new_version
        return current_version
