import inspect
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables.components import ComponentStateBase
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.extensions.moderation.workflows.interactables import ModerationComponent

TState = TypeVar("TState", bound=ComponentStateBase)

def moderation_component(
    *,
    identifier: str,
    is_bound: bool = False,
    is_ephemeral: bool = False,
    required_permissions: Permission = Permission.NONE,
    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE,
    defer_type: DeferType = DeferType.NONE
) -> Callable[[Callable[[Any, InteractionContext, TState], Awaitable[InteractionResponse]]], Callable[[Any, InteractionContext, TState], Awaitable[InteractionResponse]]]:
    def wrapper(
        target: Callable[[Any, InteractionContext, TState], Awaitable[InteractionResponse]]
    ) -> Callable[[Any, InteractionContext, TState], Awaitable[InteractionResponse]]:
        func_params = inspect.signature(target).parameters
        param_names = tuple(func_params.keys())

        setattr(target, DECORATOR_METADATA_NAME, ModerationComponent(
            callback = target,
            identifier=identifier,
            state_type=func_params[param_names[2]].annotation,
            is_bound=is_bound,
            is_ephemeral=is_ephemeral,
            required_permissions=required_permissions,
            required_moderator_permissions=required_moderator_permissions,
            defer_type=defer_type
        ))
        return target
    return wrapper
