from typing import Any, Callable, Coroutine, Optional, Tuple

from ..models import Option
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables import Command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

def command(
    *,
    description: str,
    name: Optional[str] = None,
    group_name: Optional[str] = None,
    subgroup_name: Optional[str] = None,
    options: Tuple[Option, ...] = (),
    is_bound: bool = False,
    is_ephemeral: bool = False,
    required_permissions: Permission = Permission.NONE,
    defer_type: DeferType = DeferType.NONE
):
    """A decorator that can be used to conveniently turn a function
    of a workflow into a command interaction.

    :param description: The user-friendly description of the command.
    :type description: str
    :param name: The name of the command, defaults to None
    :type name: Optional[str], optional
    :param group_name: The optional name of the group the command belongs to, defaults to None
    :type group_name: Optional[str], optional
    :param subgroup_name: The optional nem fo the subgroup the command belongs to, defaults to None
    :type subgroup_name: Optional[str], optional
    :param options: The list of command arguments, defaults to ()
    :type options: Tuple[Option, ...], optional
    :param is_bound: Whether only the invoking user can interact with the result, defaults to False
    :type is_bound: bool, optional
    :param is_ephemeral: Whether only the invoking user can see the result, defaults to False
    :type is_ephemeral: bool, optional
    :param required_permissions: Any required permissions in addition to the workflow's requirements, defaults to Permission.NONE
    :type required_permissions: Permission, optional
    :param defer_type: The type of the deferral of the response, defaults to DeferType.NONE
    :type defer_type: DeferType, optional
    """

    def wrapper(target: Callable[..., Coroutine[Any, Any, InteractionResponse]]):
        setattr(target, DECORATOR_METADATA_NAME, Command(
            callback=target,
            description=description,
            name=name or target.__name__,
            group_name=group_name,
            subgroup_name=subgroup_name,
            options=options,
            is_bound=is_bound,
            is_ephemeral=is_ephemeral,
            required_permissions=required_permissions,
            defer_type=defer_type
        ))
        return target
    return wrapper
