from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables.components import ComponentBase, LayoutBase
from holobot.sdk.utils.type_utils import UNDEFINED, UndefinedOrNoneOr
from ..models import Embed
from .action_base import ActionBase

@dataclass(kw_only=True, frozen=True)
class ContentChangingActionBase(ActionBase):
    content: UndefinedOrNoneOr[str] = UNDEFINED
    embed: UndefinedOrNoneOr[Embed] = UNDEFINED
    components: ComponentBase | list[LayoutBase] = field(default_factory=list)

    suppress_user_mentions: bool = False
    """Determines whether user mentions should avoid sending a notification."""
