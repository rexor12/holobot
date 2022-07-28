from typing import Protocol

class KernelInterface(Protocol):
    def run(self) -> None:
        ...