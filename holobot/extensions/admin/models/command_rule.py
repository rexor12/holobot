from discord.errors import Forbidden
from ..enums import RuleState
from datetime import datetime
from typing import Dict, Optional

rule_to_text_map: Dict[RuleState, str] = {
    RuleState.ALLOW: "allowed",
    RuleState.FORBID: "forbidden"
}

class CommandRule:
    def __init__(self) -> None:
        pass

    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, value: int) -> None:
        self.__id = value
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self.__created_at = value
    
    @property
    def created_by(self) -> str:
        return self.__created_by

    @created_by.setter
    def created_by(self, value: str) -> None:
        self.__created_by = value
    
    @property
    def server_id(self) -> str:
        return self.__server_id
    
    @server_id.setter
    def server_id(self, value: str) -> None:
        self.__server_id = value
    
    @property
    def state(self) -> RuleState:
        return self.__state
    
    @state.setter
    def state(self, value: RuleState) -> None:
        self.__state = value
    
    @property
    def group(self) -> Optional[str]:
        return self.__group
    
    @group.setter
    def group(self, value: Optional[str]) -> None:
        self.__group = value
    
    @property
    def command(self) -> Optional[str]:
        return self.__command
    
    @command.setter
    def command(self, value: Optional[str]) -> None:
        self.__command = value
    
    @property
    def channel_id(self) -> Optional[str]:
        return self.__channel_id
    
    @channel_id.setter
    def channel_id(self, value: Optional[str]) -> None:
        self.__channel_id = value
    
    def textify(self) -> str:
        text_bits = []
        if self.group is not None or self.command is not None:
            text_bits.append("_/")
            if self.group is not None:
                text_bits.append(self.group)
            if self.command is not None:
                if self.group is not None:
                    text_bits.append(" ")
                text_bits.append(self.command)
            text_bits.append("_ is ")
        else: text_bits.append("all commands are ")
        text_bits.append(rule_to_text_map.get(self.state, None) or self.state.__str__())
        if self.channel_id is not None:
            text_bits.append(f" in <#{self.channel_id}>")
        else: text_bits.append(" everywhere")
        text_bits.append(".")
        return ''.join(text_bits)
