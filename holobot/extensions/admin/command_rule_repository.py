from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .enums.rule_state import RuleState
from .models import CommandRule
from asyncpg.connection import Connection
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.ioc.decorators import injectable
from typing import Optional, Tuple

@injectable(CommandRuleRepositoryInterface)
class CommandRuleRepository(CommandRuleRepositoryInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get(self, id: int) -> Optional[CommandRule]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                sql, args = Query.select().columns(
                    "id", "created_at", "created_by", "server_id", "state", "command_group", "command", "channel_id"
                ).from_table("admin_rules").where("id", Equality.EQUAL, id).build()
                record = await connection.fetchrow(sql, *args)
                return CommandRuleRepository.__record_to_entity(record) if record is not None else None
    
    async def get_many(self, server_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                sql, args = Query.select().columns(
                    "id", "created_at", "created_by", "server_id", "state", "command_group", "command", "channel_id"
                ).from_table("admin_rules").where(
                    "server_id", Equality.EQUAL, server_id
                ).limit().start_index(start_offset).max_count(page_size).build()
                records = await connection.fetch(sql, *args)
                return tuple([CommandRuleRepository.__record_to_entity(record) for record in records])
    
    async def add_or_update(self, rule: CommandRule) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                sql, args = Query.update().table("admin_rules").field("created_at", rule.created_at).field("created_by", rule.created_by
                    ).field("state", rule.state).where("server_id", Equality.EQUAL, rule.server_id).build()
                id: Optional[int] = await connection.fetchval(sql, *args)
                if id is not None:
                    return id
                
                sql, args = Query.insert().table("admin_rules").field("created_at", rule.created_at).field("created_by", rule.created_by).field(
                    "server_id", rule.server_id).field("state", rule.state).field("command_group", rule.group).field("command", rule.command
                    ).field("channel_id", rule.channel_id).returning().column("id").build()
                id: Optional[int] = await connection.fetchval(sql, *args)
                if id is None:
                    raise ValueError("Unexpected error while creating a new rule.")
                return id
    
    async def get_relevant(self, server_id: str, channel_id: str, group: Optional[str], subgroup: Optional[str], command: Optional[str]) -> Tuple[CommandRule, ...]:
        raise NotImplementedError

    @staticmethod
    def __record_to_entity(record) -> CommandRule:
        entity = CommandRule()
        entity.id = record["id"]
        entity.created_at = record["created_at"]
        entity.created_by = record["created_by"]
        entity.server_id = record["server_id"]
        entity.state = RuleState(record["state"])
        entity.group = record["command_group"]
        entity.command = record["command"]
        entity.channel_id = record["channel_id"]
        return entity
