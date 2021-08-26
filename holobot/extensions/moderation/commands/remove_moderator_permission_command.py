from .moderation_command_base import ModerationCommandBase
from .responses import ModeratorPermissionsChangedResponse
from ..enums import ModeratorPermission
from ..managers import IPermissionManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveModeratorPermissionCommand(ModerationCommandBase):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__("remove")
        self.group_name = "moderation"
        self.subgroup_name = "permissions"
        self.description = "Removes a moderator permission to a user."
        self.options = [
            Option("user", "The mention of the user to modify."),
            Option("permission", "The permission to remove.", OptionType.INTEGER, choices=[
                Choice("Warn users", ModeratorPermission.WARN_USERS),
                Choice("Mute users", ModeratorPermission.MUTE_USERS),
                Choice("Kick users", ModeratorPermission.KICK_USERS),
                Choice("Ban users", ModeratorPermission.BAN_USERS)
            ])
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        self.__permission_manager: IPermissionManager = permission_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str, permission: int) -> CommandResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        typed_permission = ModeratorPermission(permission)
        await self.__permission_manager.remove_permissions(context.server_id, user_id, typed_permission)
        return ModeratorPermissionsChangedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            permission=typed_permission,
            is_addition=False,
            action=ReplyAction(content=f"{user} has had the permission to '{typed_permission.textify()}' _revoked_.")
        )
