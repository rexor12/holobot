import asyncio
from collections.abc import Callable
from typing import Any

from .cancellation_token_registration import CancellationTokenRegistration

class CancellationToken:
    """A token used for signaling cancellation requests to asynchronous operations."""

    def __init__(self) -> None:
        self.__is_cancellation_requested: bool = False
        self.__registrations: dict[int, CancellationTokenRegistration] = {}
        self.__current_registration_id = 0

    @property
    def is_cancellation_requested(self) -> bool:
        """Gets whether cancellation has been requested.

        :return: True, if cancellation has been requested.
        :rtype: bool
        """

        return self.__is_cancellation_requested

    def register(self,
                 callback: Callable[[Any], None],
                 state: Any) -> CancellationTokenRegistration:
        """Registers a method to be called when cancellation is requested.

        :param callback: The method to be called.
        :type callback: Callable[[Any], None]
        :param state: An optional object to be passed to the callback.
        :type state: Any
        :raises asyncio.InvalidStateError: Raised when the token has been cancelled already.
        :return: The descriptor of the registration.
        :rtype: CancellationTokenRegistration
        """

        if self.__is_cancellation_requested:
            raise asyncio.InvalidStateError("The token has been cancelled already.")

        current_id = self.__current_registration_id
        self.__current_registration_id += 1
        registration = CancellationTokenRegistration(current_id, callback, state)
        self.__registrations[current_id] = registration
        return registration

    def unregister(self, registration: CancellationTokenRegistration) -> bool:
        """Removes the specified registration.

        :param registration: The registration to be removed.
        :type registration: CancellationTokenRegistration
        :return: True, if the registration was found and removed.
        :rtype: bool
        """

        return self.__registrations.pop(registration.identifier, None) is not None

    def cancel(self) -> None:
        """Used internally to mark the token as cancelled and run the registrations."""

        self.__is_cancellation_requested = True
        for registration in self.__registrations.values():
            registration.callback(registration.state)
