from typing import Tuple

class ExtensionProviderInterface:
    def get_packages(self) -> Tuple[str, ...]:
        raise NotImplementedError
