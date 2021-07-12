from typing import Tuple

class DisconnectedSubGraphError(Exception):
    def __init__(self, nodes: Tuple[str, ...], *args: object) -> None:
        super().__init__(*args)
        self.__nodes: Tuple[str, ...] = nodes
    
    @property
    def nodes(self) -> Tuple[str, ...]:
        return self.__nodes
