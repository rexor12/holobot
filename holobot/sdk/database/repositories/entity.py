from typing import Protocol, TypeVar

TIdentifier = TypeVar("TIdentifier")

class Entity(Protocol[TIdentifier]):
    # NOTE By convention, only simple primary keys are supported
    # and they must be named as "id".
    id: TIdentifier

    # NOTE This empty initializer is required to avoid a false error
    # in RepositoryBase that believes IEntity has no initializer.
    def __init__(self) -> None:
        super().__init__()
