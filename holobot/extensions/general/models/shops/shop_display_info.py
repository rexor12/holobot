from dataclasses import dataclass

@dataclass(kw_only=True)
class ShopDisplayInfo:
    identifier: int
    name: str
