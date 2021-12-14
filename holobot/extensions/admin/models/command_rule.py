from ..enums import RuleState
from datetime import datetime
from typing import Dict, Optional

rule_to_text_map: Dict[RuleState, str] = {
    RuleState.ALLOW: "allowed",
    RuleState.FORBID: "forbidden"
}

rule_to_emoji_map: Dict[RuleState, str] = {
    RuleState.ALLOW: ":white_check_mark:",
    RuleState.FORBID: ":no_entry:"
}

class CommandRule:
    def __init__(self) -> None:
        self.id = -1
        self.created_at = datetime.utcnow()
        self.created_by = ""
        self.server_id = ""
        self.state = RuleState.ALLOW
        self.group = None
        self.subgroup = None
        self.command = None
        self.channel_id = None

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
    def subgroup(self) -> Optional[str]:
        return self.__subgroup
    
    @subgroup.setter
    def subgroup(self, value: Optional[str]) -> None:
        self.__subgroup = value
    
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

    def __lt__(self, other: 'CommandRule') -> bool:
        return self.__get_weight() < other.__get_weight()
    
    def textify(self) -> str:
        text_bits = [rule_to_emoji_map.get(self.state, None) or "", " "]
        if self.group is not None or self.command is not None:
            text_bits.append("`/")
            if self.group is not None:
                text_bits.append(self.group)
                if self.subgroup is not None:
                    text_bits.append(f" {self.subgroup}")
            if self.command is not None:
                if self.group is not None:
                    text_bits.append(" ")
                text_bits.append(self.command)
            text_bits.append("` is ")
        else: text_bits.append("All commands are ")
        text_bits.append(rule_to_text_map.get(self.state, "") or self.state.__str__())
        if self.channel_id is not None:
            text_bits.append(f" in <#{self.channel_id}>")
        else: text_bits.append(" everywhere")
        text_bits.append(".")
        return ''.join(text_bits)

    def __get_weight(self) -> int:
        return 1000 * int(bool(self.group)) + 100 * int(bool(self.subgroup)) + 10 * int(bool(self.command)) + int(bool(self.channel_id))
