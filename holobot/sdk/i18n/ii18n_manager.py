from typing import Protocol

class II18nManager(Protocol):
    """Interface for a service used to manage I18N related states."""

    def reload_all(self) -> None:
        """Reloads all I18N files."""
