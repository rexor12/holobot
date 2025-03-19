from typing import NamedTuple

from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.workflows.interactables.components import LayoutBase

class View(NamedTuple):
    content: str | None = None
    embed: Embed | None = None
    components: list[LayoutBase] | None = None
