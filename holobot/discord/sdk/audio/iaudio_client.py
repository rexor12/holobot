from .iaudio_source import IAudioSource

class IAudioClient:
    async def close(self) -> None:
        raise NotImplementedError
    
    async def play(self, source: IAudioSource) -> None:
        raise NotImplementedError
    
    async def stop(self) -> None:
        raise NotImplementedError
    
    def add_on_disconnect_handler(self) -> None:
        raise NotImplementedError
