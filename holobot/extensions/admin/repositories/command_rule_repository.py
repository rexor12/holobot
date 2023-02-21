from collections.abc import Awaitable, Sequence

from holobot.extensions.admin.models import CommandRule
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.queries import Query, WhereBuilder, WhereConstraintBuilder
from holobot.sdk.database.queries.constraints import (
    and_expression, column_expression, or_expression
)
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import set_time_zone
from .icommand_rule_repository import ICommandRuleRepository
from .records import CommandRuleRecord

@injectable(ICommandRuleRepository)
class CommandRuleRepository(
    RepositoryBase[int, CommandRuleRecord, CommandRule],
    ICommandRuleRepository
):
    @property
    def record_type(self) -> type[CommandRuleRecord]:
        return CommandRuleRecord

    @property
    def model_type(self) -> type[CommandRule]:
        return CommandRule

    @property
    def table_name(self) -> str:
        return "admin_rules"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def add_or_update(self, rule: CommandRule) -> int:
        async with (session := await self._get_session()):
            id: int | None = await Query.update().table(self.table_name).fields(
                ("created_at", set_time_zone(rule.created_at, None)),
                ("created_by", rule.created_by),
                ("state", rule.state)
            ).where().fields(
                Connector.AND,
                ("server_id", Equality.EQUAL, rule.server_id),
                ("command_group", Equality.EQUAL, rule.group),
                ("command_subgroup", Equality.EQUAL, rule.subgroup),
                ("command", Equality.EQUAL, rule.command),
                ("channel_id", Equality.EQUAL, rule.channel_id)
            ).returning().column("id").compile().fetchval(session.connection)
            if id is not None:
                return id

            id = await Query.insert().in_table(self.table_name).fields(
                ("created_at", set_time_zone(rule.created_at, None)),
                ("created_by", rule.created_by),
                ("server_id", rule.server_id),
                ("state", rule.state),
                ("command_group", rule.group),
                ("command_subgroup", rule.subgroup),
                ("command", rule.command),
                ("channel_id", rule.channel_id)
            ).returning().column("id").compile().fetchval(session.connection)
            if id is None:
                raise ValueError("Unexpected error while creating a new rule.")
            return id

    def get_many(
        self,
        server_id: str,
        group: str | None,
        subgroup: str | None,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[CommandRule]]:
        def get_filter(where: WhereBuilder) -> WhereConstraintBuilder:
            builder = where.field("server_id", Equality.EQUAL, server_id)
            if group is not None:
                builder = builder.and_field("command_group", Equality.EQUAL, group)
                if subgroup is not None:
                    builder = builder.and_field("command_subgroup", Equality.EQUAL, subgroup)
            return builder

        return self._paginate(
            (("id", Order.ASCENDING),),
            page_index,
            page_size,
            get_filter
        )

    async def get_relevant(
        self,
        server_id: str,
        channel_id: str,
        group: str | None,
        subgroup: str | None,
        command: str | None
    ) -> Sequence[CommandRule]:
        async with (session := await self._get_session()):
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
            if filters:
                filter_expression = or_expression(filter_expression, *filters)
            records = await Query.select().columns(
                *self.column_names
            ).from_table(self.table_name).where().expression(
                and_expression(
                    column_expression("server_id", Equality.EQUAL, server_id),
                    or_expression(
                        column_expression("channel_id", Equality.EQUAL, None),
                        column_expression("channel_id", Equality.EQUAL, channel_id)
                    ),
                    filter_expression
                )
            ).compile().fetch(session.connection)

            return tuple(
                self._map_record_to_model(self._map_query_result_to_record(record))
                for record in records
            )

    def delete_by_server(self, server_id: str) -> Awaitable[int]:
        return self._delete_by_filter(
            lambda where: where.field("server_id", Equality.EQUAL, server_id)
        )

    def _map_record_to_model(self, record: CommandRuleRecord) -> CommandRule:
        return CommandRule(
            identifier=record.id,
            created_at=record.created_at,
            created_by=record.created_by,
            server_id=record.server_id,
            state=record.state,
            group=record.command_group,
            subgroup=record.command_subgroup,
            command=record.command,
            channel_id=record.channel_id
        )

    def _map_model_to_record(self, model: CommandRule) -> CommandRuleRecord:
        return CommandRuleRecord(
            id=model.identifier,
            created_at=model.created_at,
            created_by=model.created_by,
            server_id=model.server_id,
            state=model.state,
            command_group=model.group,
            command_subgroup=model.subgroup,
            command=model.command,
            channel_id=model.channel_id
        )
