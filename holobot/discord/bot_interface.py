from discord.user import User
from typing import Optional

class BotInterface:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError
        
    async def send_dm(self, user_id: int, message: str) -> None:
        raise NotImplementedError
