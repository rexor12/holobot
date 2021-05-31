class MessagingInterface:
    async def send_dm(self, user_id: str, message: str) -> None:
        raise NotImplementedError
