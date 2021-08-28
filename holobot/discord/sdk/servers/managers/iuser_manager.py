class IUserManager:
    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        raise NotImplementedError
    
    async def ban_user(self, server_id: str, user_id: str, reason: str, delete_message_days: int = 0) -> None:
        raise NotImplementedError

    async def assign_role(self, server_id: str, user_id: str, role_id: str) -> None:
        raise NotImplementedError

    async def remove_role(self, server_id: str, user_id: str, role_id: str) -> None:
        raise NotImplementedError
