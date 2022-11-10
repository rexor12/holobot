from typing import Protocol

class IMaintenanceManager(Protocol):
    """Interface for a service used to control maintenance mode."""

    async def is_maintenance_mode_enabled(self) -> bool:
        """Determines whether maintenance mode is currently enabled.

        :return: True, if maintenance mode is enabled.
        :rtype: bool
        """
        ...

    async def set_maintenance_mode(self, is_enabled: bool) -> None:
        """Changes the operating mode of the application.

        :param is_enabled: Whether maintenance mode is to be enabled.
        :type is_enabled: bool
        """
        ...
