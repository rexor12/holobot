from __future__ import annotations

from enum import IntEnum, unique

@unique
class RuleState(IntEnum):
    ALLOW = 0
    FORBID = 1

    @staticmethod
    def parse(value: str) -> RuleState:
        return RuleState.__members__.get(value.upper(), RuleState.ALLOW)
