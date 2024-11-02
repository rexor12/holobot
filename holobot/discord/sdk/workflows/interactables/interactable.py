from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums.permission import Permission
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import RestrictionBase

@dataclass(kw_only=True)
class Interactable:
    """Defines a user interaction type."""

    callback: Callable[..., Awaitable[InteractionResponse]]
    """Determines the method that is called when
    the interaction needs to be processed.

    The arguments passed to this callback are the workflow, the interaction
    context and any custom arguments in this order.
    """

    required_permissions: Permission = Permission.NONE
    """Permissions that are required for the invocation
    in addition to those requires by the associated workflow itself.
    """

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

    restrictions: Iterable[RestrictionBase] = field(default_factory=tuple)
    """A set of server restrictions that determine
    which servers the interactable is available for.

    - If no restrictions are specified, the interactable will be available globally.
    - If multiple restrictions are specified, the interactable is available
    if and only if at least one of the restrictions allows it.
    """

    cooldown: Cooldown | None = None
    """Determines how often can the interactable be invoked."""

    extension_data: dict[str, Any] = field(default_factory=dict)
    """Contains extension specific data used by interactables.

    It is recommended to prefix the keys with a value that uniquely identifies
    the extension, such as `myext_some_key` instead of just `some_key`.
    """
