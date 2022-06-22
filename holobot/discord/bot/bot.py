from .bot_interface import BotInterface
from hikari import GatewayBot, Intents, Snowflakeish, User
from typing import Optional

class Bot(GatewayBot, BotInterface):
    def __init__(self, token: str, intents: Intents):
        super().__init__(token, intents=intents)

    # async def set_status_text(self, type: ActivityType, text: str, status: Status = None):
    #     await self.change_presence(
    #         activity=Activity(name=text, type=type),
    #         status=status
    #     )

    def get_user_by_id(self, user_id: Snowflakeish) -> Optional[User]:
        return self.cache.get_user(user_id)
    