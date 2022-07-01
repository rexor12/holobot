from .bot_interface import BotInterface
from hikari import GatewayBot, Intents, Snowflakeish, User
from typing import Optional

class Bot(GatewayBot, BotInterface):
    def __init__(self, token: str, intents: Intents):
        super().__init__(token, intents=intents)

    def get_user_by_id(self, user_id: Snowflakeish) -> Optional[User]:
        return self.cache.get_user(user_id)
    