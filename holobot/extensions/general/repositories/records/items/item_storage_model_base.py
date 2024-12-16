from dataclasses import dataclass

from holobot.sdk.serialization import json_type_hierarchy_root

@json_type_hierarchy_root()
@dataclass(kw_only=True)
class ItemStorageModelBase:
    count: int
