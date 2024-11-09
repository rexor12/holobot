from hikari import Guild

from holobot.discord.bot import get_bot
from holobot.discord.sdk.servers import IServerDataProvider
from holobot.discord.sdk.servers.models import ServerData
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none

@injectable(IServerDataProvider)
class ServerDataProvider(IServerDataProvider):
    async def get_basic_data_by_id(self, server_id: int) -> ServerData:
        assert_not_none(server_id, "server_id")

        guild = await get_bot().get_guild_by_id(server_id)
        return ServerDataProvider.__guild_to_basic_data(guild)

    @staticmethod
    def __guild_to_basic_data(guild: Guild) -> ServerData:
        return ServerData(
            server_id=guild.id,
            icon_url=str(guild.icon_url) if guild.icon_url else None,
            banner_url=guild.banner_url.url if guild.banner_url else None,
            name=guild.name,
            owner_id=guild.owner_id
        )
