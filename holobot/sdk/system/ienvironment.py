from typing import Protocol

from .models import Version

class IEnvironment(Protocol):
    @property
    def root_path(self) -> str:
        ...

    @property
    def version(self) -> Version:
        ...
