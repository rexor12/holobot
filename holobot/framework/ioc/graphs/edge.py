from .tnode import TNode
from typing import Generic

class Edge(Generic[TNode]):
    def __init__(self, source: TNode, target: TNode) -> None:
        super().__init__()
        self.__source: TNode = source
        self.__target: TNode = target
    
    @property
    def source(self) -> TNode:
        return self.__source
    
    @property
    def target(self) -> TNode:
        return self.__target
    
    def __eq__(self, o: object) -> bool:
        if not type(o) == Edge or not isinstance(o, Edge):
            return False
        return self.__source == o.__source and self.__target == o.__target
