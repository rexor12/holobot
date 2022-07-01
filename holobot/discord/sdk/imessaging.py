from abc import ABCMeta, abstractmethod

class IMessaging(metaclass=ABCMeta):
    @abstractmethod
    async def send_private_message(self, user_id: str, message: str) -> None:
        ...

    @abstractmethod
    async def send_channel_message(self, server_id: str, channel_id: str, message: str) -> None:
        ...
