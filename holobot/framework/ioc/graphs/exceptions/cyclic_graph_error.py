from typing import Any, Set

class CyclicGraphError(Exception):
    def __init__(self, nodes: Set[Any], *args: object) -> None:
        super().__init__(*args)
        self.__nodes: Set[Any] = nodes
    
    @property
    def nodes(self) -> Set[Any]:
        return self.__nodes
