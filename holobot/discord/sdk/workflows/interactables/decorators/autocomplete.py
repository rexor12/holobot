from collections.abc import Awaitable, Callable

from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables import Autocomplete
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

def autocomplete(
    *,
    command_name: str,
    options: str | tuple[str, ...] = (),
    group_name: str | None = None,
    subgroup_name: str | None = None
):
    """A decorator that can be used to conveniently turn a function
    of a workflow into an autocomplete interaction.

    :param command_name: The name of the command, defaults to None
    :type command_name: str | None, optional
    :param options: The names of the options the decorated resolver supports, defaults to ()
    :type options: str | tuple[str, ...], optional
    :param group_name: The optional name of the group the command belongs to, defaults to None
    :type group_name: str | None, optional
    :param subgroup_name: The optional name of the subgroup the command belongs to, defaults to None
    :type subgroup_name: str | None, optional
    """

    def wrapper(target: Callable[..., Awaitable[InteractionResponse]]):
        setattr(target, DECORATOR_METADATA_NAME, Autocomplete(
            callback=target,
            name=command_name,
            group_name=group_name,
            subgroup_name=subgroup_name,
            options=options if isinstance(options, tuple) else (options,)
        ))
        return target
    return wrapper
