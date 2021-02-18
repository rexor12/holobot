class DisplayInterface:
    async def send_dm(self, user_id: int, message: str):
        raise NotImplementedError
