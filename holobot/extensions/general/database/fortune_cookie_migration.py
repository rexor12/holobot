from pathlib import Path

from asyncpg.connection import Connection

from holobot.sdk.database.migration import MigrationBase, MigrationInterface
from holobot.sdk.database.migration.models import MigrationPlan
from holobot.sdk.ioc.decorators import injectable

@injectable(MigrationInterface)
class FortuneCookieMigration(MigrationBase):
    _TABLE_NAME = "fortune_cookies"

    def __init__(self) -> None:
        super().__init__(FortuneCookieMigration._TABLE_NAME, {
            0: MigrationPlan(0, 1, self.__initialize_table),
            1: MigrationPlan(1, 2, self.__upgrade_to_v1),
            2: MigrationPlan(2, 3, self.__upgrade_to_v2)
        }, {})

    async def __upgrade_to_v2(self, connection: Connection) -> None:
        await self._execute_script(
            connection,
            str(Path(__file__).parent.joinpath("scripts", "2_add_fortune_cookies.sql").absolute())
        )

    async def __upgrade_to_v1(self, connection: Connection) -> None:
        await self._execute_script(
            connection,
            str(Path(__file__).parent.joinpath("scripts", "1_add_fortune_cookies.sql").absolute())
        )

    async def __initialize_table(self, connection: Connection) -> None:
        await connection.execute((
            f"CREATE TABLE {FortuneCookieMigration._TABLE_NAME} ("
            " id SERIAL PRIMARY KEY,\n"
            " message VARCHAR(512) NOT NULL\n"
            ")"
        ))

        # Create a view that can be used to query the total row count,
        # because calculating it each time for random selection is expensive.
        await connection.execute((
            "CREATE MATERIALIZED VIEW fortune_cookies_metadata AS\n"
            " SELECT COUNT(*) as total_row_count\n"
            f" FROM {FortuneCookieMigration._TABLE_NAME}\n"
        ))

        # Create a function that can be set as a trigger to refresh the view.
        await connection.execute((
            "CREATE FUNCTION refresh_fortune_cookies_metadata()\n"
            " RETURNS TRIGGER LANGUAGE plpgsql\n"
            "AS $$\n"
            "BEGIN\n"
            " REFRESH MATERIALIZED VIEW fortune_cookies_metadata;\n"
            " RETURN NULL;\n"
            "END $$"
        ))

        # Create a function that can be used to query random fortune cookies.
        await connection.execute((
            "CREATE FUNCTION get_fortune_cookie()\n"
            " RETURNS TABLE(id BIGINT, message VARCHAR(512))\n"
            "AS $$\n"
            " SELECT id, message FROM fortune_cookies AS _data\n"
            " CROSS JOIN (\n"
            "  SELECT (RANDOM() * (total_row_count - 1) + 1)::bigint as _random_id FROM fortune_cookies_metadata\n"
            " ) AS _random_table\n"
            " WHERE _data.id >= _random_table._random_id\n"
            " ORDER BY _data.id\n"
            " LIMIT 1;\n"
            "$$ LANGUAGE SQL"
        ))

        # Create a trigger for the table to automatically refresh the view.
        await connection.execute((
            "CREATE TRIGGER refresh_metadata\n"
            "AFTER INSERT OR DELETE OR TRUNCATE\n"
            f"ON {FortuneCookieMigration._TABLE_NAME}\n"
            "FOR EACH STATEMENT\n"
            "EXECUTE PROCEDURE refresh_fortune_cookies_metadata()"
        ))

        # Insert the initial fortune cookies.
        await self._execute_script(
            connection,
            str(Path(__file__).parent.joinpath("scripts", "0_add_fortune_cookies.sql").absolute())
        )
