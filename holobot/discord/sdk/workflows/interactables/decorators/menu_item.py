from typing import Any, Callable, Coroutine

from ..enums import MenuType
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

def menu_item(
    *,
    name: str,
    title: str,
    menu_type: MenuType,
    index: int,
    is_bound: bool = False,
    is_ephemeral: bool = False,
    required_permissions: Permission = Permission.NONE,
    defer_type: DeferType = DeferType.NONE
):
    """A decorator that can be used to conveniently turn a function
    of a workflow into a context menu item interaction.

    :param name: The globally unique name of the context menu item.
    :type name: str
    :param title: The user-friendly title of the context menu item.
    :type title: str
    :param menu_type: The type of the context menu the menu item appears in.
    :type menu_type: MenuType
    :param index: The display order of the context menu item.
    :type index: int
    :param is_bound: Whether only the invoking user can interact with the result, defaults to False
    :type is_bound: bool, optional
    :param is_ephemeral: Whether only the invoking user can see the result, defaults to False
    :type is_ephemeral: bool, optional
    :param required_permissions: Any required permissions in addition to the workflow's requirements, defaults to Permission.NONE
    :type required_permissions: Permission, optional
    :param defer_type: The ype of the deferral of the response, defaults to DeferType.NONE
    :type defer_type: DeferType, optional
    """

    def wrapper(target: Callable[..., Coroutine[Any, Any, InteractionResponse]]):
        setattr(target, DECORATOR_METADATA_NAME, MenuItem(
            name=name,
            callback=target,
            title=title,
            menu_type=menu_type,
            index=index,
            is_bound=is_bound,
            is_ephemeral=is_ephemeral,
            required_permissions=required_permissions,
            defer_type=defer_type
        ))
        return target
    return wrapper
