from typing import Protocol

class IDebugger(Protocol):
    def is_debug_mode_enabled(self) -> bool:
        """Determines if debug mode is enabled for the application.

        The value is based on the configurations.

        Returns
        -------
        bool
            True, if debug mode is enabled.
        """
        ...
