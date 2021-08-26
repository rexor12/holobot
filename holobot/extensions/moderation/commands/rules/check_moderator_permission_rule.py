from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.discord.sdk.commands.models import ServerChatInteractionContext
from holobot.extensions.moderation.commands import ModerationCommandBase
from holobot.extensions.moderation.managers import IPermissionManager
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class CheckModeratorPermissionRule(CommandExecutionRuleInterface):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__()
        self.__permission_manager: IPermissionManager = permission_manager

    async def should_halt(self, command: CommandInterface, context: ServerChatInteractionContext) -> bool:
        if not isinstance(command, ModerationCommandBase):
            return False

        return not await self.__permission_manager.has_permissions(
            context.server_id,
            context.author_id,
            command.required_moderator_permissions
        )
