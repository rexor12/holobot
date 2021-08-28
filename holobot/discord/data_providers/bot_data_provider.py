from ..bot import BotAccessor
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IBotDataProvider)
class BotDataProvider(IBotDataProvider):
    def get_avatar_url(self) -> str:
        return str(BotAccessor.get_bot().user.avatar_url)

    def get_latency(self) -> float:
        return BotAccessor.get_bot().latency * 1000

    def get_server_count(self) -> int:
        return len(BotAccessor.get_bot().guilds)
