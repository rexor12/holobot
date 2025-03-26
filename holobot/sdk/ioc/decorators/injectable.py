from collections.abc import Callable
from typing import TypeVar

from kanata.decorators import injectable as kanata_injectable, scope as kanata_scope
from kanata.models import InjectableScopeType

T = TypeVar("T")

def injectable(contract_type: type | None) -> Callable[[type[T]], type[T]]:
    """
    Makes the marked class injectable by kanata.

    If `None` is specified as the contract type, the class's type itself
    will be used as the contract type.
    """

    def decorator(wrapped_class: type[T]) -> type[T]:
        injectable = kanata_injectable(contract_type or wrapped_class)(wrapped_class)
        scoped = kanata_scope(InjectableScopeType.SINGLETON)(injectable)
        return scoped
    return decorator
