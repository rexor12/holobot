from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.extensions.moderation.commands import ModerationCommandBase
from holobot.extensions.moderation.managers import IPermissionManager
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class CheckModeratorPermissionRule(CommandExecutionRuleInterface):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__()
        self.__permission_manager: IPermissionManager = permission_manager

    async def should_halt(self, command: CommandInterface, context: SlashContext) -> bool:
        if not isinstance(command, ModerationCommandBase):
            return False

        return not await self.__permission_manager.has_permissions(
            str(context.guild_id),
            str(context.author_id),
            command.required_moderator_permissions
        )
