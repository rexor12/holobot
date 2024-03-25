from collections.abc import Sequence
from dataclasses import dataclass, field

from holobot.extensions.general.sdk.quests.models import QuestProtoId, QuestRewardBase

@dataclass(kw_only=True)
class QuestRewardDescriptor:
    """Holds information about the received quest rewards of a user."""

    quest_proto_id: QuestProtoId
    """The identifier of the quest prototype that granted the rewards."""

    title: str | None
    """The title of the quest."""

    note: str | None
    """The note associated to the quest."""

    completion_text: str | None
    """The text displayed when the quest is completed."""

    granted_items: Sequence[QuestRewardBase] = field(default_factory=tuple)
    """The items the user has received."""

    granted_xp: int = 0
    """The amount of experience points the user received."""

    granted_sp: int = 0
    """The number of skill points the user received."""
