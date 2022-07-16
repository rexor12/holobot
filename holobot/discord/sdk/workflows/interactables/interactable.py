from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums.permission import Permission
from holobot.discord.sdk.models import InteractionContext

@dataclass(kw_only=True)
class Interactable:
    """Defines a user interaction type."""

    callback: Callable[[Any, Interactable, InteractionContext, *Any], Awaitable[Any]]
    """Determines the method that is called when
    the interaction needs to be processed.
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
