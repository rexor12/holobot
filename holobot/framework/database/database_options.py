from dataclasses import dataclass
from typing import ClassVar

from holobot.sdk.configs import OptionsDefinition

@dataclass
class DatabaseOptions(OptionsDefinition):
    section_name: ClassVar[str] = "Core"

    Host: str = "127.0.0.1"
    Port: int = 5432
    Database: str = "holobot"
    User: str = "postgres"
    Password: str = ""
    AutoCreateDatabase: bool = False
    IsSslEnabled: bool = True
