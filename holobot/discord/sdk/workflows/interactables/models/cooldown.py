from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.enums import EntityType

@dataclass(kw_only=True, frozen=True)
class Cooldown:
    """Describes the cooldown behavior of an interactable."""

    duration: int
    """The duration of the cooldown in seconds."""

    entity_type: EntityType = EntityType.USER
    """The type of the entity the cooldown is associated to."""
