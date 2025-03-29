from typing import NamedTuple

import hikari

class ChannelInfo(NamedTuple):
    channel_id: int
    thread_id: int | None

def get_channel_and_thread_ids(
    interaction: hikari.PartialInteraction
) -> ChannelInfo:

    if interaction.channel.thread_metadata:
        assert interaction.channel.parent_id
        return ChannelInfo(
            channel_id=interaction.channel.parent_id,
            thread_id=interaction.channel.id
        )

    return ChannelInfo(
        channel_id=interaction.channel_id,
        thread_id=None
    )
