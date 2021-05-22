from .models import ExportMetadata
from typing import Any, Callable, Type

def export(contract_type: Type[Any]) -> Callable[[Type[Any]], Type[Any]]:
    def decorator(wrapped_class: Type[Any]) -> Type[Any]:
        setattr(wrapped_class, ExportMetadata.PROPERTY_NAME, ExportMetadata(contract_type, wrapped_class))
        return wrapped_class

    return decorator
