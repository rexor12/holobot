from .command_rule_manager_interface import CommandRuleManagerInterface
from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .models import CommandRule
from holobot.discord.sdk.commands import CommandRegistryInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.exception_utils import assert_not_none

@injectable(CommandRuleManagerInterface)
class CommandRuleManager(CommandRuleManagerInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        #self.__repository: CommandRuleRepositoryInterface = services.get(CommandRuleRepositoryInterface)
        self.__registry: CommandRegistryInterface = services.get(CommandRegistryInterface)
        
    async def set_rule(self, rule: CommandRule) -> int:
        assert_not_none(rule.server_id, "rule.server_id")
        assert_not_none(rule.created_by, "rule.created_by")
        # TODO Validate if group/command exists.
        if rule.command is not None:
            if not self.__registry.command_exists(rule.command, rule.group):
                raise ValueError("Invalid command.")
        elif rule.group is not None:
            if not self.__registry.group_exists(rule.group):
                raise ValueError("Invalid group.")
        #rule.id = await self.__repository.add_or_update(rule)
        return rule.id
