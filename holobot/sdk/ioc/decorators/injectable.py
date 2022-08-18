from collections.abc import Callable
from typing import TypeVar

from kanata.decorators import injectable as kanata_injectable, scope as kanata_scope
from kanata.models import InjectableScopeType

T = TypeVar("T")

def injectable(contract_type: type) -> Callable[[type[T]], type[T]]:
    def decorator(wrapped_class: type[T]) -> type[T]:
        injectable = kanata_injectable(contract_type)(wrapped_class)
        scoped = kanata_scope(InjectableScopeType.SINGLETON)(injectable)
        return scoped
    return decorator
