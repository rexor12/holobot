from __future__ import annotations

from enum import IntEnum, unique

@unique
class SearchType(IntEnum):
    TEXT = 0
    IMAGE = 1

    @staticmethod
    def parse(value: str) -> SearchType:
        return SearchType.__members__.get(value.upper(), SearchType.TEXT)
