from .models import ExportMetadata
from typing import Any, Callable, List, Type

def injectable(contract_type: Type[Any]) -> Callable[[Type[Any]], Type[Any]]:
    def decorator(wrapped_class: Type[Any]) -> Type[Any]:
        metadatas: List[ExportMetadata] = getattr(wrapped_class, ExportMetadata.PROPERTY_NAME, [])
        metadatas.append(ExportMetadata(contract_type, wrapped_class))
        setattr(wrapped_class, ExportMetadata.PROPERTY_NAME, metadatas)
        return wrapped_class

    return decorator
