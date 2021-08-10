from holobot.discord.sdk.commands import CommandInterface
from holobot.sdk.reactive.models import EventBase

class CommandUsedEvent(EventBase):
    def __init__(self, command: CommandInterface, server_id: str, user_id: str) -> None:
        self.command = command
        self.server_id = server_id
        self.user_id = user_id
    
    # TODO Pass the command's group/sub-group/name instead of the entire command object.
    @property
    def command(self) -> CommandInterface:
        return self.__command
    
    @command.setter
    def command(self, value: CommandInterface) -> None:
        self.__command = value
    
    @property
    def server_id(self) -> str:
        return self.__server_id
    
    @server_id.setter
    def server_id(self, value: str) -> None:
        self.__server_id = value
    
    @property
    def user_id(self) -> str:
        return self.__user_id
    
    @user_id.setter
    def user_id(self, value: str) -> None:
        self.__user_id = value
