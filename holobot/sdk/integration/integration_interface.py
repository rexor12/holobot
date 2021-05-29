class IntegrationInterface:
    async def start(self) -> None:
        raise NotImplementedError
    
    async def stop(self) -> None:
        raise NotImplementedError
