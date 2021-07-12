from .edge import Edge
from .tnode import TNode
from holobot.sdk.exceptions import ArgumentError
from typing import Generic, List, Set, Tuple

class Graph(Generic[TNode]):
    """A basic, non-directed graph that consists of nodes and edges between them."""

    def __init__(self, allow_parallel_edges: bool = False) -> None:
        """Initializes a new instance.
        
        Initializes a new instance of ``Graph``.

        Parameters
        ----------
        allow_parallel_edges : ``bool``
            Whether multiple edges between the same two nodes are allowed.
        """

        self.__allow_parallel_edges: bool = allow_parallel_edges
        self.__nodes: Set[TNode] = set()
        self.__edges: List[Edge[TNode]] = []

    @property
    def allow_parallel_edges(self) -> bool:
        """Gets whether multiple edges between the same two nodes are allowed."""

        return self.__allow_parallel_edges

    @property
    def nodes(self) -> Set[TNode]:
        """Gets the set of nodes this graphs consist of."""

        return self.__nodes.copy()
    
    @property
    def edges(self) -> Tuple[Edge[TNode], ...]:
        """Gets the collection of edges between the nodes."""

        return tuple(self.__edges)
    
    def add_node(self, node: TNode) -> None:
        """Adds a new node to the graph.

        Adds a node that hasn't been added yet to the graph.

        Parameters
        ----------
        node : ``TNode``
            The node to be added.
        
        Raises
        ------
        ``ArgumentError``
            Raised when the node to be added is already part of the graph.
        """

        if node in self.__nodes:
            raise ArgumentError("node", "The given node is already part of the graph.")
        self.__nodes.add(node)
    
    def add_edge(self, source: TNode, target: TNode) -> None:
        """Adds an edge to the graph.

        Adds an edge that may or may have not been added yet to the graph.

        Parameters
        ----------
        source : ``TNode``
            The source node of the edge.
        
        target : ``TNode``
            The target node of the edge.
        
        Raises
        ------
        ``ArgumentError``
            Raised when parallel edges aren't allowed and an identical edge is already added.
        """

        new_edge = Edge(source, target)
        if self.__allow_parallel_edges:
            self.__edges.append(new_edge)
            return
        
        for edge in self.__edges:
            if self._is_same_edge(edge, new_edge):
                raise ArgumentError("target", f"An edge between '{source}' and '{target}' is added already.")
        self.__edges.append(new_edge)
    
    def _is_same_edge(self, existing_edge: Edge, new_edge: Edge) -> bool:
        """Determines whether two edges are equal.

        Override this method in sub-classes to determine if two edges are equal. By default,
        two edges are equal if and only if their sources and targets are equal in any combination.

        Returns
        -------
        ``bool``
            True, if the two edges are equal.
        """

        return (
            (existing_edge.source == new_edge.source and existing_edge.target == new_edge.target)
            or (existing_edge.source == new_edge.target and existing_edge.target == new_edge.source)
        )
    
    def __contains__(self, item: object) -> bool:
        return item in self.__nodes
