from discord.guild import Guild, Member

class IUserManager:
    def get_guild(self, server_id: str) -> Guild:
        raise NotImplementedError

    def get_guild_member(self, server_id: str, user_id: str) -> Member:
        raise NotImplementedError

    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        raise NotImplementedError
    
    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        raise NotImplementedError
