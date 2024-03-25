from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils import utcnow
from ..enums import RuleState

rule_to_text_map: dict[RuleState, str] = {
    RuleState.ALLOW: "allowed",
    RuleState.FORBID: "forbidden"
}

rule_to_emoji_map: dict[RuleState, str] = {
    RuleState.ALLOW: ":white_check_mark:",
    RuleState.FORBID: ":no_entry:"
}

@dataclass(kw_only=True)
class CommandRule(AggregateRoot[int]):
    identifier: int = -1
    created_at: datetime = field(default_factory=utcnow)
    created_by: str
    server_id: str
    state: RuleState = RuleState.ALLOW
    group: str | None = None
    subgroup: str | None = None
    command: str | None = None
    channel_id: str | None = None

    def __lt__(self, other: CommandRule) -> bool:
        return self.__get_weight() < other.__get_weight()

    def textify(self) -> str:
        text_bits = [rule_to_emoji_map.get(self.state, ""), " "]
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
        else:
            text_bits.append("All commands are ")
        text_bits.extend((
            rule_to_text_map.get(self.state, str(self.state)),
            f" in <#{self.channel_id}>" if self.channel_id is not None else " everywhere",
            "."
        ))
        return "".join(text_bits)

    def __get_weight(self) -> int:
        return bool(self.group) << 3 | bool(self.subgroup) << 2 | bool(self.command) << 1 | bool(self.channel_id)
