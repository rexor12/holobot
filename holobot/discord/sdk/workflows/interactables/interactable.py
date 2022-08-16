from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums.permission import Permission
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass(kw_only=True)
class Interactable:
    """Defines a user interaction type."""

    callback: Callable[..., Coroutine[Any, Any, InteractionResponse]]
    """Determines the method that is called when
    the interaction needs to be processed.

    The arguments passed to this callback are the workflow, the interaction
    context and any custom arguments in this order.
    """

    required_permissions: Permission = Permission.NONE
    """Permissions that are required for the invocation
    in addition to those requires by the associated workflow itself.
    """

    # TODO Bound interactions are currently not supported.
    is_bound: bool = False
    """Determines if the interactable is bound to the user who invoked it.

    This means that other users cannot interact with the response,
    eg. they cannot click buttons.
    """

    is_ephemeral: bool = False
    """Determines if the response of the interactable is visible
    to the user who invoked it only.
    """

    defer_type: DeferType = DeferType.NONE
    """Determines the type of deferral of the response."""

    server_ids: set[str] = field(default_factory=set)
    """A set of identifiers that specifies the servers the interactable is available in.

    If the set is empty, the interactable will be available globally.
    """
