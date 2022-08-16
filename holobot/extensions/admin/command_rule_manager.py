from .command_registry_interface import CommandRegistryInterface
from .command_rule_manager_interface import CommandRuleManagerInterface
from .command_rule_repository_interface import CommandRuleRepositoryInterface
from .enums import RuleState
from .exceptions import InvalidCommandError
from .models import CommandRule
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.exception_utils import assert_not_none
from holobot.sdk.queries import PaginationResult

@injectable(CommandRuleManagerInterface)
class CommandRuleManager(CommandRuleManagerInterface):
    def __init__(self, command_registry: CommandRegistryInterface, rule_repository: CommandRuleRepositoryInterface) -> None:
        super().__init__()
        self.__repository: CommandRuleRepositoryInterface = rule_repository
        self.__registry: CommandRegistryInterface = command_registry

    async def get_rules_by_server(self, server_id: str, page_index: int, page_size: int, group: str | None = None, subgroup: str | None = None) -> PaginationResult[CommandRule]:
        assert_not_none(server_id, "server_id")
        if subgroup is not None:
            assert_not_none(group, "group")

        return await self.__repository.get_many(server_id, group, subgroup, page_index, page_size)

    async def set_rule(self, rule: CommandRule) -> int:
        assert_not_none(rule.server_id, "rule.server_id")
        assert_not_none(rule.created_by, "rule.created_by")

        if rule.command is not None:
            if not (command := self.__registry.get_command(rule.command, rule.group, rule.subgroup)) or not command.can_disable:
                raise InvalidCommandError(rule.command, rule.group, rule.subgroup)
        elif rule.subgroup is not None:
            if (rule.group is None
                or not (subgroup := self.__registry.get_subgroup(rule.group, rule.subgroup))
                or not subgroup.can_disable):
                raise InvalidCommandError(rule.command, rule.group, rule.subgroup)
        elif rule.group is not None:
            if not (group := self.__registry.get_group(rule.group)) or not group.can_disable:
                raise InvalidCommandError(rule.command, rule.group, rule.subgroup)

        rule.id = await self.__repository.add_or_update(rule)
        return rule.id

    async def remove_rule(self, rule_id: int) -> None:
        await self.__repository.delete_by_id(rule_id)

    async def remove_rules_by_server(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        await self.__repository.delete_by_server(server_id)

    async def can_execute(self, server_id: str, channel_id: str, group: str | None, subgroup: str | None, command: str) -> bool:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(command, "command")

        command_config = self.__registry.get_command(command, group, subgroup)
        if not command_config or not command_config.can_disable:
            return True

        rules = await self.__repository.get_relevant(server_id, channel_id, group, subgroup, command)
        sorted_rules = sorted(rules, reverse=True)
        return len(sorted_rules) == 0 or sorted_rules[0].state == RuleState.ALLOW
