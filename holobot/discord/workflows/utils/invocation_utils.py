from holobot.discord.sdk.workflows.interactables import Command, Component, Interactable, MenuItem
from holobot.discord.sdk.workflows.interactables.enums import EntityType

def get_entity_id(
    interactable: Interactable,
    server_id: str | None,
    channel_id: str | None,
    user_id: str
) -> str | None:
    if not interactable.cooldown:
        return None

    entity_type = interactable.cooldown.entity_type
    id_parts = []
    # The server ID is always included (when available) to avoid cross-server cooldowns.
    if server_id:
        id_parts.append(("server", server_id))
    if entity_type is EntityType.CHANNEL and channel_id:
        id_parts.append(("channel", channel_id))
    elif entity_type is EntityType.USER:
        id_parts.append(("user", user_id))

    # Unknown interactable types share a common cooldown, otherwise it's specific.
    match interactable:
        case Command() as command:
            id_parts.append((
                "command",
                ".".join((command.group_name or "", command.subgroup_name or "", command.name))
            ))
        case Component() as component:
            id_parts.append(("component", component.identifier))
        case MenuItem() as menu_item:
            id_parts.append(("menu", menu_item.title))

    return "/".join(map(lambda i: ":".join(i), id_parts))
