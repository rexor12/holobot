
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id_or_default
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.admin import CommandRegistryInterface, CommandRuleManagerInterface
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class TestCommandWorkflow(WorkflowBase):
    def __init__(
        self,
        command_registry: CommandRegistryInterface,
        i18n_provider: II18nProvider,
        rule_manager: CommandRuleManagerInterface
    ) -> None:
        super().__init__(required_permissions=Permission.ADMINISTRATOR)
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.__i18n_provider = i18n_provider

    @command(
        description="Checks if a command can be used in the current or the specified channel.",
        name="test",
        group_name="admin",
        subgroup_name="commands",
        options=(
            Option("command", "The specific command, such as \"roll\"."),
            Option("group", "The command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The command subgroup, such as \"commands\".", is_mandatory=False),
            Option("channel", "The channel to test.", is_mandatory=False)
        )
    )
    async def test_command(
        self,
        context: ServerChatInteractionContext,
        command: str,
        group: str | None = None,
        subgroup: str | None = None,
        channel: str | None = None
    ) -> InteractionResponse:
        if context.server_id is None:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "interactions.server_only_interaction_error"
                ))
            )

        if not self.__command_registry.command_exists(command, group, subgroup):
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.admin.test_command_workflow.invalid_command_error"
                ))
            )

        channel_id = get_channel_id_or_default(channel, context.channel_id) if channel is not None else context.channel_id
        can_execute = await self.__command_rule_manager.can_execute(context.server_id, channel_id, group, subgroup, command)
        i18n_key = (
            "extensions.admin.test_command_workflow.command_can_execute"
            if can_execute
            else "extensions.admin.test_command_workflow.command_cannot_execute"
        )
        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                i18n_key,
                { "channel_id": channel_id }
            ))
        )
