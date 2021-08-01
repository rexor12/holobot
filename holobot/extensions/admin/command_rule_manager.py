from .command_registry_interface import CommandRegistryInterface
from .command_rule_manager_interface import CommandRuleManagerInterface
from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .exceptions import InvalidCommandError
from .models import CommandRule
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.exception_utils import assert_not_none
from typing import Optional, Tuple

@injectable(CommandRuleManagerInterface)
class CommandRuleManager(CommandRuleManagerInterface):
    def __init__(self, command_registry: CommandRegistryInterface, rule_repository: CommandRuleRepositoryInterface) -> None:
        super().__init__()
        self.__repository: CommandRuleRepositoryInterface = rule_repository
        self.__registry: CommandRegistryInterface = command_registry
        
    async def get_rules_by_server(self, server_id: str, start_offset: int, page_size: int) -> Tuple[CommandRule, ...]:
        assert_not_none(server_id, "server_id")
        return await self.__repository.get_many(server_id, start_offset, page_size)
        
    async def set_rule(self, rule: CommandRule) -> int:
        assert_not_none(rule.server_id, "rule.server_id")
        assert_not_none(rule.created_by, "rule.created_by")

        if rule.command is not None:
            if not (command := self.__registry.get_command(rule.command, rule.group)) or not command.can_disable:
                raise InvalidCommandError(rule.command, rule.group, None)
        elif rule.group is not None:
            if not (group := self.__registry.get_group(rule.group)) or not group.can_disable:
                raise InvalidCommandError(rule.command, rule.group, None)
        
        rule.id = await self.__repository.add_or_update(rule)
        return rule.id
    
    async def can_execute(self, group: Optional[str], subgroup: Optional[str], command: str) -> bool:
        raise NotImplementedError
