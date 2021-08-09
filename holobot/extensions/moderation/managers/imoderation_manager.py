from datetime import timedelta

class IModerationManager:
    async def mute_user(self, user_id: str, duration: timedelta, reason: str) -> None:
        raise NotImplementedError

    async def kick_user(self, user_id: str, reason: str) -> None:
        raise NotImplementedError

    async def ban_user(self, user_id: str, reason: str) -> None:
        raise NotImplementedError
    
    async def warn_user(self, user_id: str, reason: str) -> None:
        raise NotImplementedError
