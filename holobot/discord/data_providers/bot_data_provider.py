from collections.abc import Sequence

from holobot.discord.bot import get_bot
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.models import Server
from holobot.sdk.ioc.decorators import injectable

@injectable(IBotDataProvider)
class BotDataProvider(IBotDataProvider):
    def get_user_id(self) -> str:
        user = get_bot().get_me()
        return str(user.id) if user else ""

    def get_avatar_url(self) -> str:
        user = get_bot().get_me()
        return str(user.avatar_url) if user else ""

    def get_latency(self) -> float:
        return get_bot().heartbeat_latency * 1000

    def get_server_count(self) -> int:
        return len(get_bot().cache.get_available_guilds_view())

    def get_servers(self, page_index: int, page_size: int) -> tuple[int, Sequence[Server]]:
        guilds = sorted(get_bot().cache.get_available_guilds_view().items(), key=lambda i: i[0])
        offset = page_index * page_size
        if offset >= len(guilds):
            offset = 0
        count = min(len(guilds) - offset, page_size)
        if not count:
            return (len(guilds), ())

        page: list[Server] = []
        for guild_id, guild in guilds[offset:(offset + count)]:
            owner = guild.get_member(guild.owner_id)
            page.append(Server(
                identifier=str(guild_id),
                owner_id=str(guild.owner_id),
                owner_name=owner.username if owner else None,
                name=guild.name,
                member_count=guild.member_count,
                icon_url=guild.icon_url.url if guild.icon_url else None,
                is_large=guild.is_large,
                joined_at=guild.joined_at,
                shard_id=guild.shard_id
            ))

        return (len(guilds), page)
