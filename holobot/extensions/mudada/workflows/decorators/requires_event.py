from collections.abc import Awaitable, Callable

from holobot.discord.sdk.workflows.constants import DECORATOR_METADATA_NAME
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.sdk.exceptions import ArgumentError

REQUIRED_EVENT_NAME_KEY = "mudada_required_event_name"

def requires_event(
    event_name: str
):
    def wrapper(target: Callable[..., Awaitable[InteractionResponse]]):
        decorator_metadata = getattr(target, DECORATOR_METADATA_NAME)
        if not isinstance(decorator_metadata, Interactable):
            raise ArgumentError("target", "Only interactables are supported by this decorator.")

        decorator_metadata.extension_data[REQUIRED_EVENT_NAME_KEY] = event_name

        return target
    return wrapper
