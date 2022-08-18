from hikari import Guild

from holobot.discord.sdk.servers import IServerDataProvider
from holobot.discord.sdk.servers.models import ServerData
from holobot.discord.utils import get_guild
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IServerDataProvider)
class ServerDataProvider(IServerDataProvider):
    def get_basic_data_by_id(self, server_id: str) -> ServerData:
        assert_not_none(server_id, "server_id")

        guild = get_guild(server_id)
        return ServerDataProvider.__guild_to_basic_data(guild)

    @staticmethod
    def __guild_to_basic_data(guild: Guild) -> ServerData:
        return ServerData(
            server_id=str(guild.id),
            icon_url=str(guild.icon_url) if guild.icon_url else None,
            banner_url=guild.banner_url.url if guild.banner_url else None,
            name=guild.name,
            owner_id=str(guild.owner_id)
        )
