from .interactables.decorators import moderation_command
from .responses import ModeratorPermissionsChangedResponse
from ..enums import ModeratorPermission
from ..managers import IPermissionManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class AddModeratorPermissionWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        permission_manager: IPermissionManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__permission_manager = permission_manager

    @moderation_command(
        description="Assign a moderator permission to a user.",
        name="add",
        group_name="moderation",
        subgroup_name="permissions",
        options=(
            Option("user", "The mention of the user to modify."),
            Option("permission", "The permission to assign.", OptionType.INTEGER, choices=(
                Choice("Warn users", ModeratorPermission.WARN_USERS),
                Choice("Mute users", ModeratorPermission.MUTE_USERS),
                Choice("Kick users", ModeratorPermission.KICK_USERS),
                Choice("Ban users", ModeratorPermission.BAN_USERS)
            ))
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def add_moderator_Permission(
        self,
        context: ServerChatInteractionContext,
        user: str,
        permission: int
    ) -> InteractionResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )

        typed_permission = ModeratorPermission(permission)
        await self.__permission_manager.add_permissions(context.server_id, user_id, typed_permission)

        permission_i18n = self.__i18n_provider.get(
            f"extensions.moderation.permissions.{typed_permission.value}"
        )

        return ModeratorPermissionsChangedResponse(
            author_id=context.author_id,
            user_id=user_id,
            permission=typed_permission,
            is_addition=True,
            action=ReplyAction(
                suppress_user_mentions=True,
                content=self.__i18n_provider.get(
                    "extensions.moderation.add_moderator_permission_workflow.permission_assigned",
                    {
                        "user_id": user_id,
                        "permission": permission_i18n
                    }
                )
            )
        )
