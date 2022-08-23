from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout
from ..models import Embed
from .action_base import ActionBase

@dataclass(kw_only=True, frozen=True)
class ContentChangingActionBase(ActionBase):
    content: str | Embed
    components: ComponentBase | list[Layout] = field(default_factory=list)
