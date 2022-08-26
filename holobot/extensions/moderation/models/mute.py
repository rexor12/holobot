from dataclasses import dataclass

@dataclass(kw_only=True)
class Mute:
    identifier: int = -1
    server_id: str
    user_id: str
