import asyncio

from .cancellation_token import CancellationToken

class CancellationTokenSource:
    """Provides a cancellation token that can be passed to asynchronous methods."""

    def __init__(self) -> None:
        self.__is_cancelled: bool = False
        self.__token: CancellationToken = CancellationToken()

    @property
    def is_cancelled(self) -> bool:
        """Gets whether the token has been cancelled.

        :return: True, if the token has been cancelled.
        :rtype: bool
        """

        return self.__is_cancelled

    @property
    def token(self) -> CancellationToken:
        """Gets the token associated to this token source.

        :raises asyncio.InvalidStateError: Raised when the token has been cancelled already.
        :return: The associated cancellation token.
        :rtype: CancellationToken
        """

        if self.__is_cancelled:
            raise asyncio.InvalidStateError("The token has been cancelled already.")

        return self.__token

    def cancel(self) -> None:
        """Cancels the associated cancellation token."""

        self.__is_cancelled = True
        CancellationToken.cancel(self.__token)
