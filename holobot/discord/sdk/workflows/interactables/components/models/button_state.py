from dataclasses import dataclass
from typing import Any

from holobot.discord.sdk.models import Emoji
from holobot.sdk.utils.string_utils import try_parse_int
from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class ButtonState(ComponentStateBase):
    custom_data: dict[str, str]
    """Additional data used by extensions."""

    emoji: Emoji | None
    """The emoji displayed on the button, if any."""
