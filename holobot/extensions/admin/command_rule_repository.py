from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .enums.rule_state import RuleState
from .models import CommandRule
from asyncpg.connection import Connection
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Any, List, Optional, Tuple

@injectable(CommandRuleRepositoryInterface)
class CommandRuleRepository(CommandRuleRepositoryInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.__database_manager: DatabaseManagerInterface = database_manager

    async def get(self, id: int) -> Optional[CommandRule]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                record = await connection.fetchrow((
                    "SELECT id, created_at, created_by, server_id, state, command_group, command, channel_id"
                    " FROM admin_rules WHERE id = $1"
                ), id)
                return CommandRuleRepository.__record_to_entity(record) if record is not None else None
    
    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch((
                    "SELECT id, created_at, created_by, server_id, state, command_group, command, channel_id"
                    " FROM admin_rules WHERE created_by = $1 LIMIT $3 OFFSET $2"
                ), user_id, start_offset, page_size)
                return tuple([CommandRuleRepository.__record_to_entity(record) for record in records])
    
    async def add_or_update(self, rule: CommandRule) -> int:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                sql, params = CommandRuleRepository.get_update_params(rule)
                id: Optional[int] = await connection.fetchval(sql, *params)
                if id is not None:
                    return id
                
                id: Optional[int] = await connection.fetchval((
                    "INSERT INTO admin_rules (created_at, created_by, server_id, state, command_group, command, channel_id)"
                    " VALUES ($1, $2, $3, $4, $5, $6, $7)"
                    " RETURNING id"
                ), rule.created_at, rule.created_by, rule.server_id, rule.state, rule.group, rule.command, rule.channel_id)
                if id is None:
                    raise ValueError("Unexpected error while creating a new rule.")
                return id
    
    @staticmethod
    def get_update_params(rule: CommandRule) -> Tuple[str, List[str]]:
        sql = [
            "UPDATE admin_rules SET (created_at, created_by, state) = ($1, $2, $3) WHERE server_id = $4"
        ]
        params = [rule.created_at, rule.created_by, rule.state, rule.server_id]

        part, use_var = CommandRuleRepository.get_operation("command_group", rule.group, len(params) + 1)
        sql.append(part)
        if use_var:
            params.append(rule.group)

        part, use_var = CommandRuleRepository.get_operation("command", rule.command, len(params) + 1)
        sql.append(part)
        if use_var:
            params.append(rule.command)

        part, use_var = CommandRuleRepository.get_operation("channel_id", rule.channel_id, len(params) + 1)
        sql.append(part)
        if use_var:
            params.append(rule.channel_id)
        
        sql.append("RETURNING id")
        return (" ".join(sql), params)
    
    @staticmethod
    def get_operation(column: str, value: Optional[Any], parameter_index: int) -> Tuple[str, bool]:
        if value is None:
            return (f"AND {column} IS NULL", False)
        return (f"AND {column} = ${parameter_index}", True)
    
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
