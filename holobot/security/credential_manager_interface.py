from typing import Any, Dict, Type

class CredentialManagerInterface:
    def get(self, name: str, default_value: str = None, converter: Type = None) -> Any:
        raise NotImplementedError

    def get_many(self, pairs: Dict[str, str]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for name, default_value in pairs.items():
            result[name] = self.get(name, default_value)
        return result