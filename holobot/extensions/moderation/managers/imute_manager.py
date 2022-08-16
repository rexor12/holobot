from datetime import timedelta

class IMuteManager:
    async def mute_user(self, server_id: str, user_id: str, reason: str, duration: timedelta | None = None) -> None:
        raise NotImplementedError

    async def unmute_user(self, server_id: str, user_id: str, clear_auto_unmute: bool = True) -> None:
        raise NotImplementedError
