from ..bot import BotAccessor
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IBotDataProvider)
class BotDataProvider(IBotDataProvider):
    def get_user_id(self) -> str:
        user = BotAccessor.get_bot().get_me()
        return str(user.id) if user else ""

    def get_avatar_url(self) -> str:
        user = BotAccessor.get_bot().get_me()
        return str(user.avatar_url) if user else ""

    def get_latency(self) -> float:
        return BotAccessor.get_bot().heartbeat_latency * 1000

    def get_server_count(self) -> int:
        return len(BotAccessor.get_bot().cache.get_available_guilds_view())
