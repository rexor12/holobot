from enum import IntEnum, unique

@unique
class SearchType(IntEnum):
    TEXT = 0
    IMAGE = 1
    
    @staticmethod
    def parse(value: str):
        return SearchType.__dict__.get(value.upper(), SearchType.TEXT)
