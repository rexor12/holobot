from dataclasses import dataclass

@dataclass
class CommandConfiguration:
    Name: str
    CanDisable: bool = True
