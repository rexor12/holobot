from dataclasses import dataclass, field

from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.reactive.models import EventBase

@dataclass(kw_only=True, frozen=True)
class NewGiveawaysEvent(EventBase):
    giveaways: tuple[ExternalGiveawayItem, ...] = field(default_factory=tuple)
