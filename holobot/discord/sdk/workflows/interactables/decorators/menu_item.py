from collections.abc import Awaitable, Callable

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from ..enums import MenuType

def menu_item(
    *,
    title: str,
    menu_type: MenuType,
    priority: int,
    is_bound: bool = False,
    is_ephemeral: bool = False,
    required_permissions: Permission = Permission.NONE,
    defer_type: DeferType = DeferType.NONE,
    server_ids: set[str] | None = None,
    cooldown: Cooldown | None = None
):
    """A decorator that can be used to conveniently turn a function
    of a workflow into a context menu item interaction.

    :param title: The globally unique user-friendly title of the context menu item. This also serves as the identifier.
    :type title: str
    :param menu_type: The type of the context menu the menu item appears in.
    :type menu_type: MenuType
    :param priority: The priority of the menu item in the context menu.
    :type priority: int
    :param is_bound: Whether only the invoking user can interact with the result, defaults to False
    :type is_bound: bool, optional
    :param is_ephemeral: Whether only the invoking user can see the result, defaults to False
    :type is_ephemeral: bool, optional
    :param required_permissions: Any required permissions in addition to the workflow's requirements, defaults to Permission.NONE
    :type required_permissions: Permission, optional
    :param defer_type: The ype of the deferral of the response, defaults to DeferType.NONE
    :type defer_type: DeferType, optional
    :param server_ids: The identifiers of the servers the command is available in, defaults to None
    :type server_ids: set[str] | None, optional
    :param cooldown: Determines how often can the interactable be invoked.
    :type cooldown: Cooldown | None, optional
    """

    def wrapper(target: Callable[..., Awaitable[InteractionResponse]]):
        setattr(target, DECORATOR_METADATA_NAME, MenuItem(
            callback=target,
            title=title,
            menu_type=menu_type,
            priority=priority,
            is_bound=is_bound,
            is_ephemeral=is_ephemeral,
            required_permissions=required_permissions,
            defer_type=defer_type,
            server_ids=server_ids or set(),
            cooldown=cooldown
        ))
        return target
    return wrapper
