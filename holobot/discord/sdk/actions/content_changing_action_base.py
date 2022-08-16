from dataclasses import dataclass, field

from .action_base import ActionBase
from ..models import Embed
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout

@dataclass(kw_only=True, frozen=True)
class ContentChangingActionBase(ActionBase):
    content: str | Embed
    components: ComponentBase | list[Layout] = field(default_factory=lambda: [])
