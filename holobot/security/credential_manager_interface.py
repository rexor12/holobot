from typing import Callable, Dict, Optional, TypeVar

T = TypeVar("T")

# TODO Split to interface and base class (get_many is implemented here).
class CredentialManagerInterface:
    def get(self, name: str, default_value: Optional[T] = None, converter: Callable[[str], T] = str) -> Optional[T]:
        raise NotImplementedError

    def get_many(self, pairs: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {}
        for name, default_value in pairs.items():
            result[name] = self.get(name, default_value)
        return result
