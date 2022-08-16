from collections.abc import Sequence
from typing import Any

from asyncpg.connection import Connection

from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, or_expression
)
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .enums.rule_state import RuleState
from .models import CommandRule

TABLE_NAME = "admin_rules"

@injectable(CommandRuleRepositoryInterface)
class CommandRuleRepository(CommandRuleRepositoryInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def add_or_update(self, rule: CommandRule) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                id: int | None = await Query.update().table(TABLE_NAME).fields(
                    ("created_at", rule.created_at),
                    ("created_by", rule.created_by),
                    ("state", rule.state)
                ).where().fields(
                    Connector.AND,
                    ("server_id", Equality.EQUAL, rule.server_id),
                    ("command_group", Equality.EQUAL, rule.group),
                    ("command_subgroup", Equality.EQUAL, rule.subgroup),
                    ("command", Equality.EQUAL, rule.command),
                    ("channel_id", Equality.EQUAL, rule.channel_id)
                ).returning().column("id").compile().fetchval(connection)
                if id is not None:
                    return id

                id = await Query.insert().in_table(TABLE_NAME).fields(
                    ("created_at", rule.created_at),
                    ("created_by", rule.created_by),
                    ("server_id", rule.server_id),
                    ("state", rule.state),
                    ("command_group", rule.group),
                    ("command_subgroup", rule.subgroup),
                    ("command", rule.command),
                    ("channel_id", rule.channel_id)
                ).returning().column("id").compile().fetchval(connection)
                if id is None:
                    raise ValueError("Unexpected error while creating a new rule.")
                return id

    async def get(self, id: int) -> CommandRule | None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await Query.select().columns(
                    "id", "created_at", "created_by", "server_id", "state", "command_group", "command_subgroup", "command", "channel_id"
                ).from_table(TABLE_NAME).where().field(
                    "id", Equality.EQUAL, id
                ).compile().fetchrow(connection)
                return CommandRuleRepository.__record_to_entity(record) if record is not None else None

    async def get_many(
        self,
        server_id: str,
        group: str | None,
        subgroup: str | None,
        page_index: int,
        page_size: int
    ) -> PaginationResult[CommandRule]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                query = Query.select().columns(
                    "id", "created_at", "created_by", "server_id", "state", "command_group", "command_subgroup", "command", "channel_id"
                ).from_table(TABLE_NAME).where().field(
                    "server_id", Equality.EQUAL, server_id
                )
                if group is not None:
                    query = query.and_field("command_group", Equality.EQUAL, group)
                    if subgroup is not None:
                        query = query.and_field("command_subgroup", Equality.EQUAL, subgroup)
                result = await (query
                    .paginate("id", page_index, page_size)
                    .compile()
                    .fetch(connection)
                )

                return PaginationResult(
                    result.page_index,
                    result.page_size,
                    result.total_count,
                    [CommandRuleRepository.__record_to_entity(record) for record in result.records]
                )

    async def get_relevant(
        self,
        server_id: str,
        channel_id: str,
        group: str | None,
        subgroup: str | None,
        command: str | None
    ) -> Sequence[CommandRule]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                filters = []
                if group is not None:
                    filters.append(
                        and_expression(
                            column_expression("command_group", Equality.EQUAL, group),
                            column_expression("command_subgroup", Equality.EQUAL, None),
                            column_expression("command", Equality.EQUAL, None)
                        )
                    )
                if subgroup is not None:
                    filters.append(
                        and_expression(
                            column_expression("command_group", Equality.EQUAL, group),
                            column_expression("command_subgroup", Equality.EQUAL, subgroup),
                            column_expression("command", Equality.EQUAL, None)
                        )
                    )
                if command is not None:
                    filters.append(
                        and_expression(
                            column_expression("command_group", Equality.EQUAL, group),
                            column_expression("command_subgroup", Equality.EQUAL, subgroup),
                            column_expression("command", Equality.EQUAL, command)
                        )
                    )
                filter_expression = and_expression(
                    column_expression("command_group", Equality.EQUAL, None),
                    column_expression("command_subgroup", Equality.EQUAL, None),
                    column_expression("command", Equality.EQUAL, None)
                )
                if len(filters) > 0:
                    filter_expression = or_expression(
                        filter_expression,
                        *filters
                    )
                records = await Query.select().columns(
                    "id", "created_at", "created_by", "server_id", "state", "command_group", "command_subgroup", "command", "channel_id"
                ).from_table(TABLE_NAME).where().expression(
                    and_expression(
                        column_expression("server_id", Equality.EQUAL, server_id),
                        or_expression(
                            column_expression("channel_id", Equality.EQUAL, None),
                            column_expression("channel_id", Equality.EQUAL, channel_id)
                        ),
                        filter_expression
                    )
                ).compile().fetch(connection)
                return tuple([CommandRuleRepository.__record_to_entity(record) for record in records])

    async def delete_by_id(self, rule_id: int) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field("id", Equality.EQUAL, rule_id).compile().execute(connection)

    async def delete_by_server(self, server_id: str) -> None:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                await Query.delete().from_table(TABLE_NAME).where().field("server_id", Equality.EQUAL, server_id).compile().execute(connection)

    @staticmethod
    def __record_to_entity(record: dict[str, Any]) -> CommandRule:
        entity = CommandRule()
        entity.id = record["id"]
        entity.created_at = record["created_at"]
        entity.created_by = record["created_by"]
        entity.server_id = record["server_id"]
        entity.state = RuleState(record["state"])
        entity.group = record["command_group"]
        entity.subgroup = record["command_subgroup"]
        entity.command = record["command"]
        entity.channel_id = record["channel_id"]
        return entity
