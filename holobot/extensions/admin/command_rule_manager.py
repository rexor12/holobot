from .command_rule_manager_interface import CommandRuleManagerInterface
from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .exceptions import InvalidCommandError
from .models import CommandRule
from holobot.discord.sdk.commands import CommandRegistryInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.exception_utils import assert_not_none

@injectable(CommandRuleManagerInterface)
class CommandRuleManager(CommandRuleManagerInterface):
    def __init__(self, command_registry: CommandRegistryInterface) -> None:
        super().__init__()
        #self.__repository: CommandRuleRepositoryInterface = services.get(CommandRuleRepositoryInterface)
        self.__registry: CommandRegistryInterface = command_registry
        
    async def set_rule(self, rule: CommandRule) -> int:
        assert_not_none(rule.server_id, "rule.server_id")
        assert_not_none(rule.created_by, "rule.created_by")
        if rule.command is not None:
            if not self.__registry.command_exists(rule.command, rule.group):
                raise InvalidCommandError(rule.command, rule.group, None)
        elif rule.group is not None:
            if not self.__registry.group_exists(rule.group):
                raise InvalidCommandError(rule.command, rule.group, None)
        #rule.id = await self.__repository.add_or_update(rule)
        return rule.id
