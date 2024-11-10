from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from ..enums import ModeratorPermission
from ..managers import IPermissionManager
from .interactables.decorators import moderation_command
from .responses import ModeratorPermissionsChangedResponse

@injectable(IWorkflow)
class RemoveModeratorPermissionWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        permission_manager: IPermissionManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__permission_manager = permission_manager

    @moderation_command(
        description="Removes a moderator permission to a user.",
        name="remove",
        group_name="moderation",
        subgroup_name="permissions",
        options=(
            Option("user", "The user to modify.", OptionType.USER),
            Option("permission", "The permission to remove.", OptionType.INTEGER, choices=(
                Choice("Warn users", ModeratorPermission.WARN_USERS),
                Choice("Mute users", ModeratorPermission.MUTE_USERS),
                Choice("Kick users", ModeratorPermission.KICK_USERS),
                Choice("Ban users", ModeratorPermission.BAN_USERS)
            ))
        ),
        required_permissions=Permission.ADMINISTRATOR
    )
    async def remove_moderator_permission(
        self,
        context: InteractionContext,
        user: int,
        permission: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        user_id = user
        typed_permission = ModeratorPermission(permission)
        await self.__permission_manager.remove_permissions(context.server_id, user_id, typed_permission)

        permission_i18n = self.__i18n_provider.get(
            f"extensions.moderation.permissions.{typed_permission.value}"
        )
        return ModeratorPermissionsChangedResponse(
            author_id=context.author_id,
            user_id=user_id,
            permission=typed_permission,
            is_addition=False,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.remove_moderator_permission_workflow.permission_revoked",
                    {
                        "user_id": user_id,
                        "permission": permission_i18n
                    }
                ),
                suppress_user_mentions=True
            )
        )
