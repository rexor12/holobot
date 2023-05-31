from dataclasses import dataclass

from .interactable import Interactable

@dataclass(kw_only=True)
class Modal(Interactable):
    identifier: str
    """The globally unique identifier of the modal.

    The same identifier CANNOT be used by multiple modals to avoid ambiguity.
    """

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.identifier})"
