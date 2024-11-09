from collections.abc import Awaitable
from datetime import timedelta
from typing import Protocol

SILENCE_DURATION_MIN = timedelta(seconds=1)
"""The minimum value allowed to be used for silencing a user."""

SILENCE_DURATION_MAX = timedelta(days=27)
"""The maximum value allowed to be used for silencing a user."""

class IUserManager(Protocol):
    """Interface for a service that provides methods for managing users."""

    def silence_user(
        self,
        server_id: int,
        user_id: int,
        duration: timedelta | None = None
    ) -> Awaitable[None]:
        """Temporarily strips the specified user of their rights
        to send messages, add reactions, etc. in the specified server.

        :param server_id: The identifier of the server in which to silence the user.
        :type server_id: int
        :param user_id: The identifier of the user to silence.
        :type user_id: int
        :param duration: The duration of the silence, defaults to None
        :type duration: timedelta | None, optional
        """
        ...

    def kick_user(self, server_id: int, user_id: int, reason: str) -> Awaitable[None]:
        """Kicks the specified user from the specified server.

        :param server_id: The identifier of the server to kick the user from.
        :type server_id: int
        :param user_id: The identifier of the user to be kicked.
        :type user_id: int
        :param reason: The reason the user is being kicked.
        :type reason: str
        """
        ...

    def ban_user(
        self,
        server_id: int,
        user_id: int,
        reason: str,
        delete_message_days: int = 0
    ) -> Awaitable[None]:
        """Bans the specified user from the specified server.

        :param server_id: The identifier of the server to ban the user from.
        :type server_id: int
        :param user_id: The identifier of the user to be banned.
        :type user_id: int
        :param reason: The reason the user is being banned.
        :type reason: str
        :param delete_message_days: An optional number of days through which to delete the user's messages, defaults to 0
        :type delete_message_days: int, optional
        """
        ...

    def has_role(self, server_id: int, user_id: int, role_id: int) -> Awaitable[bool]:
        ...

    def get_role_ids(self, server_id: int, user_id: int) -> Awaitable[set[int]]:
        ...

    def assign_role(self, server_id: int, user_id: int, role_id: int) -> Awaitable[None]:
        """Assigns the specified role to the specified user in the specified server.

        :param server_id: The identifier of the server.
        :type server_id: int
        :param user_id: The identifier of the user.
        :type user_id: int
        :param role_id: The identifier of the server-specific role.
        :type role_id: int
        """
        ...

    def remove_role(self, server_id: int, user_id: int, role_id: int) -> Awaitable[None]:
        """Removes the specified role from the specified user in the specified server.

        :param server_id: The identifier of the server.
        :type server_id: int
        :param user_id: The identifier of the user.
        :type user_id: int
        :param role_id: The identifier of the server-specific role.
        :type role_id: int
        """
        ...

    def unsilence_user(
        self,
        server_id: int,
        user_id: int
    ) -> Awaitable[None]:
        """Restores the specified user's rights
        to send messages, add reactions, etc. in the specified server.

        If the user wasn't silenced, calling this method won't change anything.

        :param server_id: The identifier of the server.
        :type server_id: int
        :param user_id: The identifier of the user.
        :type user_id: int
        """
        ...
