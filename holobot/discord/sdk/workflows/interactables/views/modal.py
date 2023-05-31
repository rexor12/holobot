from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables.components import ComponentBase
from .view_base import ViewBase

@dataclass(kw_only=True)
class Modal(ViewBase):
    title: str
    components: list[ComponentBase] = field(default_factory=list)
