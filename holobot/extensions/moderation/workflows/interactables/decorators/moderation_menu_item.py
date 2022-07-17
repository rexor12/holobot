from typing import Any, Awaitable, Callable, Coroutine

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.extensions.moderation.workflows.interactables import ModerationMenuItem

def moderation_menu_item(
    *,
    title: str,
    menu_type: MenuType,
    priority: int,
    is_bound: bool = False,
    is_ephemeral: bool = False,
    required_permissions: Permission = Permission.NONE,
    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE,
    defer_type: DeferType = DeferType.NONE
):
    def wrapper(target: Callable[..., Coroutine[Any, Any, Any]]):
        setattr(target, DECORATOR_METADATA_NAME, ModerationMenuItem(
            callback=target,
            title=title,
            menu_type=menu_type,
            priority=priority,
            is_bound=is_bound,
            is_ephemeral=is_ephemeral,
            required_permissions=required_permissions,
            required_moderator_permissions=required_moderator_permissions,
            defer_type=defer_type
        ))
        return target
    return wrapper
